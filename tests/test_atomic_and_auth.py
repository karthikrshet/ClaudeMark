"""Tests for atomic file writes and HTTP server Bearer authentication."""

import json
import os
import urllib.request
import urllib.error
import pytest
from claudemark.provenance.base import safe_atomic_write_bytes, safe_atomic_write_text


def test_safe_atomic_write_text(tmp_path):
    dest = tmp_path / "atomic_sample.txt"
    safe_atomic_write_text(dest, "Atomic write content")
    assert dest.is_file()
    assert dest.read_text(encoding="utf-8") == "Atomic write content"


def test_safe_atomic_write_bytes(tmp_path):
    dest = tmp_path / "atomic_sample.bin"
    safe_atomic_write_bytes(dest, b"\x00\x01\x02\x03\x04")
    assert dest.is_file()
    assert dest.read_bytes() == b"\x00\x01\x02\x03\x04"


def test_server_bearer_auth(running_claudemark_server, monkeypatch):
    # Public endpoints work without auth
    req = urllib.request.Request(f"{running_claudemark_server}/health")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200

    # Configure server key requirement
    monkeypatch.setenv("CLAUDEMARK_SERVER_API_KEY", "secret-token-12345")

    # Request without token should return 401
    post_data = json.dumps({"text": "Test"}).encode("utf-8")
    req_unauth = urllib.request.Request(
        f"{running_claudemark_server}/api/analyze",
        data=post_data,
        headers={"Content-Type": "application/json"},
    )
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(req_unauth)
    assert exc_info.value.code == 401

    # Request with valid Bearer token should succeed
    req_auth = urllib.request.Request(
        f"{running_claudemark_server}/api/analyze",
        data=post_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer secret-token-12345",
        },
    )
    with urllib.request.urlopen(req_auth) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "watermark_analysis" in data
