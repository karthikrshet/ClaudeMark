"""Regression tests for portable evidence bundles and MCP stdio interoperability."""

from __future__ import annotations

import io
import json
import sys

from claudemark.mcp_server import serve_stdio
from claudemark.provenance.evidence import create_evidence_bundle, verify_evidence_bundle


def test_evidence_bundle_is_verifiable(tmp_path):
    target = tmp_path / "sample.txt"
    target.write_text("Forensic evidence sample", encoding="utf-8")
    bundle = tmp_path / "evidence.zip"

    created = create_evidence_bundle(target, {"suspicious": False}, bundle, include_original=True)

    assert bundle.is_file()
    assert created["manifest"]["target"]["name"] == "sample.txt"
    assert verify_evidence_bundle(bundle)["valid"] is True


def test_mcp_tools_list_protocol(monkeypatch):
    request = {"jsonrpc": "2.0", "id": 7, "method": "tools/list", "params": {}}
    output = io.StringIO()
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(request) + "\n"))
    monkeypatch.setattr(sys, "stdout", output)

    serve_stdio()

    response = json.loads(output.getvalue())
    assert response["id"] == 7
    assert any(tool["name"] == "analyze_watermark" for tool in response["result"]["tools"])
