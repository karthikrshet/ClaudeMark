"""CLI integration tests for ClaudeMark."""

import json
from pathlib import Path
import pytest
from claudemark.cli import main


def test_cli_version(capsys):
    ret = main(["version"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "ClaudeMark" in captured.out
    assert "claude" in captured.out


def test_cli_analyze_text_terminal(capsys):
    ret = main(["analyze", "--text", "Sample prose for testing the CLI terminal output formatting."])
    assert ret == 0
    captured = capsys.readouterr()
    assert "ClaudeMark Analysis Report" in captured.out
    assert "Text Statistics" in captured.out
    assert "Unicode Forensics" in captured.out


def test_cli_analyze_text_json(capsys):
    ret = main(["analyze", "--text", "Sample text for JSON output.", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["tool"] == "ClaudeMark"
    assert "text_statistics" in data
    assert "watermark_analysis" in data


def test_cli_normalize_text(capsys):
    ret = main(["normalize", "--text", "Test\u200b with\u00a0invisibles."])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.out == "Test with invisibles."


def test_cli_diff(tmp_path, capsys):
    f1 = tmp_path / "orig.txt"
    f2 = tmp_path / "proc.txt"
    f1.write_text("Hello\u200b world first.", encoding="utf-8")
    f2.write_text("Hello world first.", encoding="utf-8")

    ret = main(["diff", str(f1), str(f2), "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["command"] == "diff"
    assert data["diff"]["anomalies_removed"] == 1


def test_cli_experimental(capsys):
    ret = main(["experimental"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "ClaudeMark Experimental Research Engine" in captured.out
