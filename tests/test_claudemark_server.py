"""Unit and integration tests for self-contained claudemark.server."""

import base64
import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
import pytest

from claudemark.server import ClaudeMarkHandler


@pytest.fixture
def running_claudemark_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), ClaudeMarkHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    base_url = f"http://127.0.0.1:{port}"
    yield base_url
    server.shutdown()


def test_claudemark_server_health(running_claudemark_server):
    req = urllib.request.Request(f"{running_claudemark_server}/health")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["ok"] is True
        assert data["service"] == "ClaudeMark"


def test_claudemark_server_capabilities(running_claudemark_server):
    req = urllib.request.Request(f"{running_claudemark_server}/capabilities")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "claude" in data["detectors"]
        assert "pdf" in data["supported_document_formats"]
        assert "png" in data["supported_image_formats"]


def test_claudemark_server_openapi(running_claudemark_server):
    req = urllib.request.Request(f"{running_claudemark_server}/openapi.json")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["openapi"] == "3.0.3"
        assert data["info"]["title"] == "ClaudeMark service"


def test_claudemark_server_inspect_endpoint(running_claudemark_server):
    sample_text = "Hidden\u200b steganography".encode("utf-8")
    b64 = base64.b64encode(sample_text).decode("ascii")
    payload = json.dumps({"file": b64, "name": "sample.txt"}).encode("utf-8")

    req = urllib.request.Request(
        f"{running_claudemark_server}/inspect",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["ok"] is True
        assert data["suspicious"] is True
        assert data["report"]["unicode_anomalies"] == 1


def test_claudemark_server_clean_endpoint(running_claudemark_server):
    sample_text = "Hidden\u200b steganography".encode("utf-8")
    b64 = base64.b64encode(sample_text).decode("ascii")
    payload = json.dumps({"file": b64, "name": "sample.txt"}).encode("utf-8")

    req = urllib.request.Request(
        f"{running_claudemark_server}/clean",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["ok"] is True
        cleaned_text = base64.b64decode(data["cleaned"]).decode("utf-8")
        assert cleaned_text == "Hidden steganography"


def test_claudemark_server_documented_file_api_aliases(running_claudemark_server):
    sample_text = "Hidden\u200b steganography".encode("utf-8")
    payload = json.dumps({
        "file": base64.b64encode(sample_text).decode("ascii"),
        "name": "sample.txt",
    }).encode("utf-8")

    for endpoint in ("/api/inspect", "/api/clean", "/api/security/scan"):
        req = urllib.request.Request(
            f"{running_claudemark_server}{endpoint}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True
