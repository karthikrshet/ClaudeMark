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
import re
import shutil
import sys
import tempfile
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from . import __version__, analyze_text, compute_forensic_diff, normalize_text
from .core.constants import MAX_INPUT_BYTES, MAX_TEXT_LENGTH
from .core.normalizer import NormalizationOptions
from .detectors.registry import detector_registry
from .provenance.base import validate_safe_path
from .provenance.batch import clean_single_file, inspect_single_file
from .web.app import get_static_asset


_ALLOWED_EXTENSIONS = {
    ".txt", ".text", ".md", ".markdown", ".html", ".htm",
    ".pdf", ".docx", ".odt", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".avif", ".heic"
}


def _get_safe_extension(raw_name: str) -> str:
    """Extract and validate file extension against strict whitelist."""
    base_name = os.path.basename(str(raw_name or "input.bin"))
    clean_name = re.sub(r"[^a-zA-Z0-9_.-]", "", base_name)
    ext = Path(clean_name).suffix.lower()
    return ext if ext in _ALLOWED_EXTENSIONS else ".bin"


class ClaudeMarkHandler(BaseHTTPRequestHandler):
    """HTTP request handler for ClaudeMark."""

    server_version = f"ClaudeMark/{__version__}"
    timeout = 15

    def log_message(self, format: str, *args: Any) -> None:
        """Safely log messages without crashing on closed/invalid stderr handles."""
        try:
            sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))
            sys.stderr.flush()
        except Exception:
            pass

    def _check_auth(self, path: str) -> bool:
        """Verify API key authentication if CLAUDEMARK_SERVER_API_KEY is configured."""
        required_key = os.environ.get("CLAUDEMARK_SERVER_API_KEY")
        if not required_key:
            return True
        # Allow static assets and health check without token
        if path in ("/", "/health", "/favicon.ico") or path.startswith("/static/"):
            return True
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            return token == required_key
        return False

    def _get_cors_origin(self) -> str:
        """Resolve allowed CORS origin from configuration without reflecting untrusted headers."""
        allowed = os.environ.get("CLAUDEMARK_CORS_ORIGIN", "*").strip()
        if not allowed or allowed == "*":
            return "*"
        # Whitelist check: strictly return an exact entry from the pre-configured server whitelist
        req_origin = re.sub(r"[\r\n\x00-\x1f]", "", self.headers.get("Origin", "")).strip()
        allowed_list = [re.sub(r"[\r\n\x00-\x1f]", "", o.strip()) for o in allowed.split(",") if o.strip()]
        for trusted_origin in allowed_list:
            if req_origin == trusted_origin:
                return trusted_origin
        return allowed_list[0] if allowed_list else "*"

    def _send_json(self, status: int, data: Any) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", self._get_cors_origin())
        self.end_headers()
        self.wfile.write(payload)
        self.wfile.flush()

    def _send_bytes(self, status: int, content_type: str, data: bytes | str) -> None:
        raw = data.encode("utf-8") if isinstance(data, str) else data
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", self._get_cors_origin())
        self.end_headers()
        self.wfile.write(raw)
        self.wfile.flush()

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", self._get_cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        if not self._check_auth(path):
            self._send_json(401, {"error": "Unauthorized: Invalid or missing API key"})
            return

        if path == "/health":
            self._send_json(200, {"status": "ok", "ok": True, "version": __version__, "service": "ClaudeMark"})
            return

        if path == "/ready":
            from .agent.tools import AGENT_TOOLS_MANIFEST
            self._send_json(200, {
                "ready": True,
                "status": "ready",
                "version": __version__,
                "detectors": detector_registry.list_detectors(),
                "detectors_count": len(detector_registry.list_detectors()),
                "tools_count": len(AGENT_TOOLS_MANIFEST),
                "zero_egress": True,
            })
            return

        if path == "/version":
            self._send_json(200, {
                "version": __version__,
                "author": "Karthik R Shet",
                "repository": "https://github.com/karthikrshet/ClaudeMark",
                "zero_egress": True,
            })
            return

        if path == "/favicon.ico":
            # Return standard empty favicon response with 204 No Content
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return

        if path == "/capabilities":
            from .agent.tools import AGENT_TOOLS_MANIFEST
            from .pixel.registry import pixel_registry

            caps = {
                "version": __version__,
                "detectors": detector_registry.list_detectors(),
                "pixel_backends": pixel_registry.list_details(),
                "supported_document_formats": ["pdf", "docx", "odt", "html", "md", "txt"],
                "supported_image_formats": ["png", "jpeg", "jpg", "webp", "svg", "avif", "heic"],
                "agent_tools": [t["name"] for t in AGENT_TOOLS_MANIFEST],
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
                    "description": "Multi-AI watermark research, provenance forensics, and security platform.",
                },
                "paths": {
                    "/health": {"get": {"summary": "Health check"}},
                    "/ready": {"get": {"summary": "Readiness probe"}},
                    "/version": {"get": {"summary": "Service version"}},
                    "/capabilities": {"get": {"summary": "List capabilities and plugins"}},
                    "/inspect": {"post": {"summary": "Inspect file (base64 envelope)"}},
                    "/clean": {"post": {"summary": "Clean file (base64 envelope)"}},
                    "/api/analyze": {"post": {"summary": "Analyze text for watermarks"}},
                    "/api/normalize": {"post": {"summary": "Normalize text and strip invisible characters"}},
                    "/api/diff": {"post": {"summary": "Forensic diff between texts"}},
                    "/api/unicode/analyze": {"post": {"summary": "Deep Unicode anomaly inspection"}},
                    "/api/unicode/visualize": {"post": {"summary": "Make invisible characters visible"}},
                    "/api/rewrite": {"post": {"summary": "Best-effort statistical watermark disruption"}},
                    "/api/evaluate": {"post": {"summary": "Before/after watermark evaluation"}},
                    "/api/security/scan": {"post": {"summary": "Defensive security scan for bombs/macros"}},
                    "/api/agent/tools": {"get": {"summary": "List AI Agent tool declarations"}},
                    "/api/agent/exec": {"post": {"summary": "Execute AI Agent tool locally"}},
                },
            })
            return

        # Serve static assets and Web UI
        asset = get_static_asset(path)
        if asset:
            data, ctype = asset
            self._send_bytes(200, ctype, data)
            return

        self._send_json(404, {"ok": False, "error": {"code": "NOT_FOUND", "message": f"Not found: {path}"}})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        length = int(self.headers.get("Content-Length", 0))
        req_id = f"req-{uuid.uuid4().hex[:12]}"

        if not self._check_auth(path):
            if length > 0:
                try:
                    self.rfile.read(min(length, 4096))
                except Exception:
                    pass
            self._send_json(401, {
                "ok": False,
                "schema_version": "1.0",
                "request_id": req_id,
                "error": {"code": "UNAUTHORIZED", "message": "Invalid or missing API key"},
            })
            return

        if length > MAX_INPUT_BYTES:
            if length > 0:
                try:
                    self.rfile.read(min(length, 4096))
                except Exception:
                    pass
            self._send_json(413, {
                "ok": False,
                "schema_version": "1.0",
                "request_id": req_id,
                "error": {"code": "PAYLOAD_TOO_LARGE", "message": f"Payload exceeds {MAX_INPUT_BYTES} bytes limit"},
            })
            return

        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            req_data = json.loads(body.decode("utf-8", errors="replace")) if body else {}
        except Exception:
            self._send_json(400, {
                "ok": False,
                "schema_version": "1.0",
                "request_id": req_id,
                "error": {"code": "MALFORMED_JSON", "message": "Invalid JSON body payload"},
            })
            return

        if path == "/api/analyze":
            text = str(req_data.get("text", ""))
            alg = str(req_data.get("algorithm", "claude"))
            thresh = req_data.get("threshold", None)

            if len(text) > MAX_TEXT_LENGTH:
                self._send_json(413, {
                    "ok": False,
                    "schema_version": "1.0",
                    "request_id": req_id,
                    "error": {"code": "PAYLOAD_TOO_LARGE", "message": f"Text length ({len(text)} chars) exceeds {MAX_TEXT_LENGTH} limit"},
                })
                return

            if alg not in detector_registry.list_detectors():
                self._send_json(400, {
                    "ok": False,
                    "schema_version": "1.0",
                    "request_id": req_id,
                    "error": {"code": "INVALID_ARGUMENT", "message": f"Unknown detector: '{alg}'. Available: {detector_registry.list_detectors()}"},
                })
                return

            if thresh is not None:
                try:
                    thresh = float(thresh)
                    if not (0.0 <= thresh <= 1.0):
                        raise ValueError("Threshold must be between 0.0 and 1.0")
                except ValueError as ve:
                    self._send_json(400, {
                        "ok": False,
                        "schema_version": "1.0",
                        "request_id": req_id,
                        "error": {"code": "INVALID_ARGUMENT", "message": str(ve)},
                    })
                    return

            res = analyze_text(text, detector_name=alg, threshold=thresh)
            self._send_json(200, {
                "ok": True,
                "schema_version": "1.0",
                "request_id": req_id,
                "tool": "ClaudeMark",
                "version": __version__,
                "result": {
                    "text_statistics": res["text_statistics"].to_dict(),
                    "unicode_forensics": res["unicode_forensics"].to_dict(),
                    "watermark_analysis": res["watermark_result"].to_dict(),
                },
                "text_statistics": res["text_statistics"].to_dict(),
                "unicode_forensics": res["unicode_forensics"].to_dict(),
                "watermark_analysis": res["watermark_result"].to_dict(),
            })
            return

        if path == "/api/unicode/analyze":
            from .core.unicode_forensics import analyze_unicode_forensics
            text = str(req_data.get("text", ""))
            if len(text) > MAX_TEXT_LENGTH:
                self._send_json(413, {
                    "ok": False,
                    "schema_version": "1.0",
                    "request_id": req_id,
                    "error": {"code": "PAYLOAD_TOO_LARGE", "message": f"Text length exceeds {MAX_TEXT_LENGTH} limit"},
                })
                return
            rep = analyze_unicode_forensics(text)
            self._send_json(200, {
                "ok": True,
                "schema_version": "1.0",
                "request_id": req_id,
                "tool": "analyze_unicode",
                "result": rep.to_dict(),
                **rep.to_dict(),
            })
            return

        if path == "/api/unicode/visualize":
            from .core.unicode_forensics import visualize_unicode_markers
            text = str(req_data.get("text", ""))
            if len(text) > MAX_TEXT_LENGTH:
                self._send_json(413, {
                    "ok": False,
                    "schema_version": "1.0",
                    "request_id": req_id,
                    "error": {"code": "PAYLOAD_TOO_LARGE", "message": f"Text length exceeds {MAX_TEXT_LENGTH} limit"},
                })
                return
            self._send_json(200, {
                "ok": True,
                "schema_version": "1.0",
                "request_id": req_id,
                "tool": "visualize_unicode",
                "result": {"visualized": visualize_unicode_markers(text)},
                "visualized": visualize_unicode_markers(text),
            })
            return

        if path == "/api/rewrite":
            from .rewrite.paraphrase import disrupt_watermark
            text = str(req_data.get("text", ""))
            if len(text) > MAX_TEXT_LENGTH:
                self._send_json(413, {
                    "ok": False,
                    "schema_version": "1.0",
                    "request_id": req_id,
                    "error": {"code": "PAYLOAD_TOO_LARGE", "message": f"Text length exceeds {MAX_TEXT_LENGTH} limit"},
                })
                return
            strat = str(req_data.get("strategy", "synonym_cadence"))
            alg = str(req_data.get("algorithm", "claude"))
            res = disrupt_watermark(text, strategy=strat, detector_name=alg)
            self._send_json(200, {
                "ok": True,
                "schema_version": "1.0",
                "request_id": req_id,
                "tool": "disrupt_watermark",
                "result": res.to_dict(),
                **res.to_dict(),
            })
            return

        if path == "/api/evaluate":
            from .rewrite.evaluation import evaluate_rewrite
            orig = str(req_data.get("original", ""))
            proc = str(req_data.get("processed", ""))
            alg = str(req_data.get("algorithm", "claude"))
            ev = evaluate_rewrite(orig, proc, detector_name=alg)
            self._send_json(200, {
                "ok": True,
                "schema_version": "1.0",
                "request_id": req_id,
                "tool": "evaluate_rewrite",
                "result": ev.to_dict(),
                **ev.to_dict(),
            })
            return

        if path == "/api/agent/tools":
            from .agent.tools import AGENT_TOOLS_MANIFEST
            self._send_json(200, {
                "ok": True,
                "schema_version": "1.0",
                "request_id": req_id,
                "tools": AGENT_TOOLS_MANIFEST,
            })
            return

        if path == "/api/agent/exec":
            from .agent.tools import AGENT_TOOLS_MANIFEST, execute_agent_tool
            # Support both tool/args and tool_name/arguments shapes
            tool_name = str(req_data.get("tool") or req_data.get("tool_name") or req_data.get("name") or "").strip()
            args_obj = req_data.get("args") if "args" in req_data else req_data.get("arguments", {})

            if not isinstance(args_obj, dict):
                self._send_json(400, {
                    "ok": False,
                    "schema_version": "1.0",
                    "request_id": req_id,
                    "error": {"code": "INVALID_ARGUMENT", "message": "Field 'args' must be a JSON object."},
                })
                return

            valid_tools = [t["name"] for t in AGENT_TOOLS_MANIFEST]
            if not tool_name or tool_name not in valid_tools:
                self._send_json(400, {
                    "ok": False,
                    "schema_version": "1.0",
                    "request_id": req_id,
                    "error": {"code": "UNKNOWN_TOOL", "message": f"Unknown tool: '{tool_name}'. Allowed tools: {valid_tools}"},
                })
                return

            try:
                result = execute_agent_tool(tool_name, args_obj)
                self._send_json(200, {
                    "ok": True,
                    "schema_version": "1.0",
                    "request_id": req_id,
                    "tool": tool_name,
                    "result": result,
                })
            except Exception as ex:
                self._send_json(400, {
                    "ok": False,
                    "schema_version": "1.0",
                    "request_id": req_id,
                    "error": {"code": "EXECUTION_FAILED", "message": str(ex)},
                })
            return

        if path == "/api/normalize":
            text = str(req_data.get("text", ""))
            res = normalize_text(text)
            self._send_json(200, {
                "ok": True,
                "schema_version": "1.0",
                "request_id": req_id,
                "tool": "normalize_text",
                "result": res.to_dict(),
                **res.to_dict(),
            })
            return

        if path == "/api/diff":
            orig = str(req_data.get("original", ""))
            proc = str(req_data.get("processed", ""))
            diff = compute_forensic_diff(orig, proc)
            self._send_json(200, {
                "ok": True,
                "schema_version": "1.0",
                "request_id": req_id,
                "tool": "ClaudeMark",
                "command": "diff",
                "result": diff.to_dict(),
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
                safe_td = validate_safe_path(td)
                tp = validate_safe_path(safe_td / f"upload_payload{safe_ext}", base_dir=safe_td)
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
                safe_td = validate_safe_path(td)
                in_p = validate_safe_path(safe_td / f"input_payload{safe_ext}", base_dir=safe_td)
                out_p = validate_safe_path(safe_td / f"cleaned_payload{safe_ext}", base_dir=safe_td)
                in_p.write_bytes(raw_bytes)
                rep = clean_single_file(in_p, out_p)
                cleaned_bytes = out_p.read_bytes() if out_p.is_file() else raw_bytes
                b64_str = base64.b64encode(cleaned_bytes).decode("ascii")
                self._send_json(200, {
                    "ok": True,
                    "cleaned": b64_str,
                    "cleaned_file_base64": b64_str,
                    "cleaned_size_bytes": len(cleaned_bytes),
                    "report": rep.to_dict(),
                })
            return

        self._send_json(404, {"error": f"Endpoint not found: {path}"})


def run_server(host: str | None = None, port: int | None = None) -> None:
    """Start ClaudeMark HTTP server."""
    actual_host = host or os.environ.get("CLAUDEMARK_HOST", "127.0.0.1")
    actual_port = port if port is not None else int(os.environ.get("CLAUDEMARK_PORT", "8950"))

    ThreadingHTTPServer.allow_reuse_address = True
    server = ThreadingHTTPServer((actual_host, actual_port), ClaudeMarkHandler)
    server.daemon_threads = True
    print(f"ClaudeMark Server listening on http://{actual_host}:{actual_port}/", flush=True)
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down ClaudeMark server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    default_host = os.environ.get("CLAUDEMARK_HOST", "127.0.0.1")
    default_port = int(os.environ.get("CLAUDEMARK_PORT", "8950"))

    parser = argparse.ArgumentParser(description="Run ClaudeMark HTTP server")
    parser.add_argument("--host", default=default_host, help="Host interface to bind")
    parser.add_argument("--port", type=int, default=default_port, help="Port to listen on")
    args = parser.parse_args()
    run_server(args.host, args.port)
