"""Self-contained HTTP service and REST API for ClaudeMark.

Endpoints:
    GET  /               -> Interactive Web Dashboard
    GET  /static/*       -> Web UI static assets (styles.css, app.js)
    GET  /health         -> Health check JSON
    GET  /capabilities   -> Supported tools, formats, and detectors
    GET  /openapi.json   -> OpenAPI 3.0.3 schema
    POST /inspect        -> Legacy Base64 inspection endpoint
    POST /clean          -> Legacy Base64 cleaning endpoint
    POST /api/analyze    -> Raw JSON text analysis & watermark detection
    POST /api/normalize  -> Raw JSON text normalization
    POST /api/diff       -> Raw JSON forensic diff
    POST /api/inspect    -> Raw JSON file inspection
    POST /api/clean      -> Raw JSON file cleaning

Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import sys
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from . import __version__, analyze_text, compute_forensic_diff, normalize_text
from .core.normalizer import NormalizationOptions
from .detectors.registry import detector_registry
from .provenance.batch import clean_single_file, inspect_single_file
from .web.app import get_static_asset

MAX_INPUT_BYTES = 100 * 1024 * 1024  # 100 MB


_ALLOWED_EXTENSIONS = {
    ".txt", ".text", ".md", ".markdown", ".html", ".htm",
    ".pdf", ".docx", ".odt", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".avif", ".heic"
}


def _get_safe_extension(raw_name: str) -> str:
    """Extract and validate file extension against strict whitelist."""
    ext = Path(raw_name).suffix.lower()
    return ext if ext in _ALLOWED_EXTENSIONS else ".bin"


class ClaudeMarkHandler(BaseHTTPRequestHandler):
    """HTTP request handler for ClaudeMark."""

    server_version = f"ClaudeMark/{__version__}"

    def _send_json(self, status: int, data: Any) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _send_bytes(self, status: int, content_type: str, data: bytes | str) -> None:
        raw = data.encode("utf-8") if isinstance(data, str) else data
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        if path == "/health":
            self._send_json(200, {"ok": True, "version": __version__, "service": "ClaudeMark"})
            return

        if path == "/capabilities":
            caps = {
                "version": __version__,
                "detectors": detector_registry.list_detectors(),
                "supported_document_formats": ["pdf", "docx", "odt", "html", "md", "txt"],
                "supported_image_formats": ["png", "jpeg", "jpg", "webp", "svg"],
                "system_tools": {
                    "c2patool": shutil.which("c2patool") is not None,
                    "exiftool": shutil.which("exiftool") is not None,
                    "qpdf": shutil.which("qpdf") is not None,
                },
            }
            self._send_json(200, caps)
            return

        if path == "/openapi.json":
            self._send_json(200, {
                "openapi": "3.0.3",
                "info": {
                    "title": "ClaudeMark service",
                    "version": __version__,
                    "description": "Multi-AI watermark research and provenance forensics service.",
                },
                "paths": {
                    "/health": {"get": {"summary": "Health check"}},
                    "/capabilities": {"get": {"summary": "List capabilities"}},
                    "/inspect": {"post": {"summary": "Inspect file (base64 envelope)"}},
                    "/clean": {"post": {"summary": "Clean file (base64 envelope)"}},
                    "/api/analyze": {"post": {"summary": "Analyze text"}},
                    "/api/normalize": {"post": {"summary": "Normalize text"}},
                    "/api/diff": {"post": {"summary": "Diff texts"}},
                },
            })
            return

        # Serve static assets and Web UI
        asset = get_static_asset(path)
        if asset:
            data, ctype = asset
            self._send_bytes(200, ctype, data)
            return

        self._send_json(404, {"error": f"Not found: {path}"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_INPUT_BYTES:
            self._send_json(413, {"error": f"Payload too large (max {MAX_INPUT_BYTES} bytes)"})
            return

        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            req_data = json.loads(body.decode("utf-8", errors="replace")) if body else {}
        except Exception:
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        if path == "/api/analyze":
            text = req_data.get("text", "")
            alg = req_data.get("algorithm", "claude")
            thresh = req_data.get("threshold", None)
            res = analyze_text(text, detector_name=alg, threshold=thresh)
            self._send_json(200, {
                "tool": "ClaudeMark",
                "version": __version__,
                "text_statistics": res["text_statistics"].to_dict(),
                "unicode_forensics": res["unicode_forensics"].to_dict(),
                "watermark_analysis": res["watermark_result"].to_dict(),
            })
            return

        if path == "/api/normalize":
            text = req_data.get("text", "")
            res = normalize_text(text)
            self._send_json(200, res.to_dict())
            return

        if path == "/api/diff":
            orig = req_data.get("original", "")
            proc = req_data.get("processed", "")
            diff = compute_forensic_diff(orig, proc)
            self._send_json(200, {
                "tool": "ClaudeMark",
                "command": "diff",
                "diff": diff.to_dict(),
            })
            return

        if path == "/inspect":
            file_b64 = req_data.get("file", "")
            raw_name = req_data.get("name", "input.bin")
            safe_ext = _get_safe_extension(raw_name)

            try:
                raw_bytes = base64.b64decode(file_b64)
            except Exception:
                self._send_json(400, {"error": "Invalid base64 payload in 'file'"})
                return

            with tempfile.TemporaryDirectory() as td:
                # Use fixed filename with validated extension inside temp sandbox
                tp = Path(td) / f"upload_payload{safe_ext}"
                tp.write_bytes(raw_bytes)
                rep = inspect_single_file(tp)
                self._send_json(200, {"ok": True, "suspicious": rep.suspicious, "report": rep.to_dict()})
            return

        if path == "/clean":
            file_b64 = req_data.get("file", "")
            raw_name = req_data.get("name", "input.bin")
            safe_ext = _get_safe_extension(raw_name)

            try:
                raw_bytes = base64.b64decode(file_b64)
            except Exception:
                self._send_json(400, {"error": "Invalid base64 payload in 'file'"})
                return

            with tempfile.TemporaryDirectory() as td:
                # Use fixed filenames with validated extensions inside temp sandbox
                in_p = Path(td) / f"input_payload{safe_ext}"
                out_p = Path(td) / f"cleaned_payload{safe_ext}"
                in_p.write_bytes(raw_bytes)
                rep = clean_single_file(in_p, out_p)
                cleaned_bytes = out_p.read_bytes() if out_p.is_file() else raw_bytes
                self._send_json(200, {
                    "ok": True,
                    "cleaned": base64.b64encode(cleaned_bytes).decode("ascii"),
                    "report": rep.to_dict(),
                })
            return

        self._send_json(404, {"error": f"Endpoint not found: {path}"})


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Start ClaudeMark HTTP server."""
    server = ThreadingHTTPServer((host, port), ClaudeMarkHandler)
    print(f"ClaudeMark Server listening on http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down ClaudeMark server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ClaudeMark HTTP server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on")
    args = parser.parse_args()
    run_server(args.host, args.port)
