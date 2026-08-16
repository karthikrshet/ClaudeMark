"""Smoke tests verifying every CLI command documented in the README."""

import json
from claudemark.cli import main


def test_cli_analyze_command(capsys):
    ret = main(["analyze", "--text", "In conclusion, it is important to analyze comprehensive paradigms.", "--algorithm", "claude"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "ClaudeMark" in captured.out or "Analysis" in captured.out


def test_cli_unicode_inspect(capsys):
    ret = main(["unicode", "inspect", "--text", "Secret\u200bText\u00a0Hidden"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Zero-Width" in captured.out


def test_cli_unicode_visualize(capsys):
    ret = main(["unicode", "visualize", "--text", "Secret\u200bText\u202eRTL"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "<ZWSP>" in captured.out
    assert "<RLO>" in captured.out


def test_cli_unicode_clean(capsys):
    ret = main(["unicode", "clean", "--text", "Secret\u200bText\u00a0Hidden"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "SecretText Hidden" in captured.out


def test_cli_rewrite_command(capsys):
    ret = main(["rewrite", "--text", "Furthermore, it is crucial to implement this.", "--strategy", "synonym_cadence"])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.out != ""


def test_cli_evaluate_command(tmp_path, capsys):
    f1 = tmp_path / "f1.txt"
    f2 = tmp_path / "f2.txt"
    f1.write_text("This is original text.", encoding="utf-8")
    f2.write_text("This is rewritten text.", encoding="utf-8")
    ret = main(["evaluate", str(f1), str(f2)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Forensic Evaluation" in captured.out


def test_cli_agent_list(capsys):
    ret = main(["agent", "list"])
    assert ret == 0
    captured = capsys.readouterr()
    tools = json.loads(captured.out)
    assert isinstance(tools, list)
    assert any(t["name"] == "analyze_watermark" for t in tools)


def test_cli_agent_exec(capsys):
    ret = main(["agent", "exec", "analyze_unicode", "--args", '{"text":"Test\\u200bData"}'])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["zero_width_count"] == 1


def test_cli_security_scan(tmp_path, capsys):
    f = tmp_path / "safe.txt"
    f.write_text("Safe file content", encoding="utf-8")
    ret = main(["security", str(f)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Threat Level: NONE" in captured.out


def test_cli_c2pa_inspect(tmp_path, capsys):
    f = tmp_path / "dummy.png"
    f.write_bytes(b"\x89PNG\r\n\x1a\n")
    ret = main(["c2pa", str(f)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Provenance Hierarchy" in captured.out
