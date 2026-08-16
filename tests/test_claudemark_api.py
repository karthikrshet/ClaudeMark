"""API and Web UI integration tests for ClaudeMark HTTP server."""

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
import pytest

from claudemark.server import ClaudeMarkHandler


@pytest.fixture
def running_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), ClaudeMarkHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    base_url = f"http://127.0.0.1:{port}"
    yield base_url
    server.shutdown()


def test_server_serves_web_ui(running_server):
    req = urllib.request.Request(f"{running_server}/")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        assert "text/html" in resp.headers.get("Content-Type")
        body = resp.read().decode("utf-8")
        assert "ClaudeMark" in body
        assert "Multi-AI Watermark" in body or "Forensics Toolkit" in body


def test_server_api_analyze(running_server):
    payload = json.dumps({"text": "The solar system contains eight planets orbiting the sun."}).encode("utf-8")
    req = urllib.request.Request(
        f"{running_server}/api/analyze",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["tool"] == "ClaudeMark"
        assert "text_statistics" in data
        assert "watermark_analysis" in data


def test_server_api_normalize(running_server):
    payload = json.dumps({"text": "Clean\u200b this\u00a0text"}).encode("utf-8")
    req = urllib.request.Request(
        f"{running_server}/api/normalize",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["normalized_text"] == "Clean this text"
        assert data["zero_width_removed"] == 1


def test_server_api_diff(running_server):
    payload = json.dumps({
        "original": "Original\u200b version",
        "processed": "Original version",
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{running_server}/api/diff",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["command"] == "diff"
        assert data["diff"]["anomalies_removed"] == 1
