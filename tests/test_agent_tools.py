"""Tests for AI Agent tool manifests, dispatching, and zero-egress execution."""

import pytest
from claudemark.agent.tools import AGENT_TOOLS_MANIFEST, execute_agent_tool


def test_agent_tools_manifest():
    names = [t["name"] for t in AGENT_TOOLS_MANIFEST]
    assert "analyze_watermark" in names
    assert "analyze_unicode" in names
    assert "inspect_provenance" in names
    assert "clean_file" in names
    assert "disrupt_watermark" in names
    assert "scan_security" in names
    assert "get_capabilities" in names


def test_agent_tool_execution_watermark():
    res = execute_agent_tool("analyze_watermark", {
        "text": "This is a clean test paragraph with natural variance.",
        "algorithm": "claude",
    })
    assert "watermark_analysis" in res
    assert "signal_score" in res["watermark_analysis"]


def test_agent_tool_execution_unicode():
    res = execute_agent_tool("analyze_unicode", {
        "text": "Secret\u200bText\u00a0Hidden",
        "visualize": True,
    })
    assert res["zero_width_count"] == 1
    assert "<ZWSP>" in res["visualized_text"]


def test_agent_tool_execution_disrupt():
    res = execute_agent_tool("disrupt_watermark", {
        "text": "Furthermore, it is crucial to implement this.",
        "strategy": "synonym_cadence",
    })
    assert res["success"] is True
    assert "rewritten_text" in res


def test_agent_tool_execution_security_scan():
    res = execute_agent_tool("scan_security", {"file_path": "README.md"})
    assert res["file_name"] == "README.md"
    assert "is_safe" in res
