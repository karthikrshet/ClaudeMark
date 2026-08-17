"""Comprehensive production hardening test suite for ClaudeMark v2.1.1.

Validates all P0/P1/P2 fixes:
- CLI --version flag and agent subcommands
- composite_score API field presence and correctness
- normalize_text_str convenience wrapper
- Real rewrite transformations and metric computation
- OASIS SARIF v2.1.0 build_sarif_report export
- claudemark.pixel.backends module import
- Path traversal sanitization and control char blocking
- Dynamic package version reporting
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import claudemark
from claudemark import (
    analyze_text,
    normalize_text,
    normalize_text_str,
)
from claudemark.agent.tools import AGENT_TOOLS_MANIFEST, execute_agent_tool
from claudemark.cli import main
from claudemark.detectors.registry import detector_registry
from claudemark.provenance.base import _sanitize_raw_path, validate_safe_path
from claudemark.provenance.sarif import build_sarif_report, convert_audit_report_to_sarif
from claudemark.reports.json_report import format_json_report
from claudemark.rewrite.paraphrase import disrupt_watermark


class TestCliFlagsAndAgent:
    """Test CLI version options and agent subcommands."""

    def test_cli_version_flag_caps(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "claudemark" in captured.out
        assert claudemark.__version__ in captured.out

    def test_cli_short_version_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit) as exc:
            main(["-V"])
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert claudemark.__version__ in captured.out

    def test_cli_agent_tools_alias(self, capsys: pytest.CaptureFixture[str]) -> None:
        code = main(["agent", "tools"])
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        tool_names = [t["name"] for t in data]
        assert "analyze_watermark" in tool_names
        assert "inspect_provenance" in tool_names

    def test_cli_agent_exec_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        code = main(["agent", "exec", "--tool", "get_capabilities", "--args", "{}"])
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "detectors" in data
        assert "tools" in data

    def test_cli_agent_exec_positional(self, capsys: pytest.CaptureFixture[str]) -> None:
        code = main(["agent", "exec", "get_capabilities"])
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "detectors" in data


class TestCompositeScoreAndApi:
    """Test composite_score alias and API ergonomics."""

    def test_detection_result_composite_score(self) -> None:
        detector = detector_registry.get("claude")
        res = detector.detect("Furthermore, this sophisticated reasoning illustrates complex paradigms.")
        assert hasattr(res, "composite_score")
        assert res.composite_score == res.signal_score
        assert isinstance(res.composite_score, float)
        assert "composite_score" in res.to_dict()
        assert "is_watermarked" in res.to_dict()

    def test_watermark_result_composite_score(self) -> None:
        from claudemark.watermark.claude_detector import ClaudeWatermarkAnalyzer
        analyzer = ClaudeWatermarkAnalyzer()
        res = analyzer.analyze("Sample analysis text")
        assert hasattr(res, "composite_score")
        assert res.composite_score == res.signal_score
        assert "composite_score" in res.to_dict()
        assert "is_watermarked" in res.to_dict()

    def test_analyze_text_watermark_result(self) -> None:
        res = analyze_text("Furthermore, this analysis demonstrates significant depth.")
        wm = res["watermark_result"]
        assert hasattr(wm, "composite_score")
        assert wm.composite_score == wm.signal_score
        d = wm.to_dict()
        assert d["composite_score"] == wm.signal_score

    def test_normalize_text_str(self) -> None:
        text = "Hello\u200b \u200cWorld\ufeff"
        cleaned_str = normalize_text_str(text)
        assert isinstance(cleaned_str, str)
        assert "\u200b" not in cleaned_str
        assert "\u200c" not in cleaned_str
        assert "\ufeff" not in cleaned_str
        assert "Hello World" in cleaned_str


class TestRewriteDisruption:
    """Test that the rewrite disruption engine actually transforms text."""

    def test_disrupt_watermark_transforms_text(self) -> None:
        sample = (
            "Furthermore, it is important to note that this comprehensive analysis "
            "demonstrates sophisticated reasoning across multiple domains. The synthesis "
            "of diverse perspectives enables nuanced understanding."
        )
        res = disrupt_watermark(sample, strategy="synonym_cadence", seed=42)
        assert res.success is True
        assert res.rewritten_text != sample
        assert res.disrupted_text == res.rewritten_text
        assert res.evaluation is not None
        assert res.evaluation.words_changed > 0
        assert res.evaluation.characters_changed > 0
        assert res.evaluation.word_change_ratio > 0.0
        assert res.evaluation.semantic_similarity > 0.7
        assert "words_changed" in res.to_dict()
        assert "disrupted_text" in res.to_dict()

    def test_disrupt_watermark_empty(self) -> None:
        res = disrupt_watermark("")
        assert res.success is True
        assert res.rewritten_text == ""


class TestPixelBackendsModule:
    """Test claudemark.pixel.backends module import and exports."""

    def test_pixel_backends_import(self) -> None:
        import claudemark.pixel.backends as backends
        assert hasattr(backends, "SynthIDImageBackend")
        assert hasattr(backends, "CtrlRegenBackend")
        assert hasattr(backends, "pixel_registry")
        all_backends = backends.list_backends()
        assert "synthid-image" in all_backends
        assert "ctrlregen" in all_backends


class TestSarifReportBuilder:
    """Test SARIF 2.1.0 report generation with polymorphic inputs."""

    def test_build_sarif_from_findings_list(self) -> None:
        findings = [
            {
                "finding_type": "ZeroWidthSteganography",
                "details": "Hidden ZWSP detected in text header",
                "file_path": "sample.txt",
                "line_number": 1,
            },
            {
                "finding_type": "ContainerSecurityThreat",
                "details": "Zip decompression ratio exceeded 100x limit",
                "file_path": "payload.zip",
                "line_number": 1,
            }
        ]
        sarif = build_sarif_report(findings)
        assert sarif["version"] == "2.1.0"
        assert len(sarif["runs"]) == 1
        results = sarif["runs"][0]["results"]
        assert len(results) == 2
        assert results[0]["ruleId"] == "CM001-ZeroWidthSteganography"
        assert results[0]["level"] == "error"
        assert results[1]["ruleId"] == "CM004-ContainerSecurityThreat"


class TestSecurityPathSanitization:
    """Test path sanitization edge cases."""

    def test_null_byte_rejection(self) -> None:
        with pytest.raises(ValueError, match="illegal control characters or null bytes"):
            _sanitize_raw_path("file\x00name.txt")

    def test_control_character_rejection(self) -> None:
        with pytest.raises(ValueError, match="illegal control characters or null bytes"):
            _sanitize_raw_path("file\x1b[31m.txt")

    def test_empty_path_rejection(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            _sanitize_raw_path("")

    def test_path_containment_violation(self, tmp_path: Path) -> None:
        base = tmp_path / "sandbox"
        base.mkdir()
        with pytest.raises(ValueError, match="Path traversal detected"):
            validate_safe_path("../../etc/passwd", base_dir=base)

    def test_path_containment_success(self, tmp_path: Path) -> None:
        base = tmp_path / "sandbox"
        base.mkdir()
        target = base / "safe.txt"
        target.write_text("safe content")
        safe_p = validate_safe_path(target, base_dir=base)
        assert safe_p == target.resolve()


class TestDynamicJsonReportVersion:
    """Test that format_json_report uses the actual package version."""

    def test_json_report_version(self) -> None:
        from claudemark.core.text_stats import analyze_text_statistics
        from claudemark.core.unicode_forensics import analyze_unicode_forensics
        from claudemark.watermark.claude_detector import ClaudeWatermarkAnalyzer

        text = "Sample test text."
        stats = analyze_text_statistics(text)
        uni = analyze_unicode_forensics(text)
        wm = ClaudeWatermarkAnalyzer().analyze(text)

        report_json = format_json_report(stats, uni, wm)
        data = json.loads(report_json)
        assert data["version"] == claudemark.__version__
        assert data["version"] != "0.1.0"


class TestSelfTestAndV22Hardenings:
    """Test 9-point self-test diagnostic, escaped CLI input, and C2PA precision."""

    def test_run_selftest_passes(self) -> None:
        from claudemark.core.selftest import run_selftest
        report = run_selftest()
        assert report.overall_status == "PASS"
        assert report.passed_checks == 9
        assert report.failed_checks == 0
        assert len(report.steps) == 9

    def test_cli_selftest_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        code = main(["selftest"])
        assert code == 0
        captured = capsys.readouterr()
        assert "SYSTEM VERIFIED" in captured.out
        assert "9/9 checks passed" in captured.out

    def test_cli_text_escaped_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        code = main(["unicode", "inspect", "--text-escaped", r"Test\u200bData\ufeff", "--json"])
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["total_anomalies"] == 2
        assert data["has_anomalies"] is True

    def test_c2pa_markdown_not_flagged(self, tmp_path: Path) -> None:
        from claudemark.provenance.documents import inspect_document
        doc_file = tmp_path / "README.md"
        doc_file.write_text("# C2PA Content Credentials Guide\nThis document describes c2pa manifests.", encoding="utf-8")
        rep = inspect_document(doc_file)
        assert rep.has_c2pa is False
        assert rep.suspicious is False

    def test_benchmark_suite_non_empty_f1(self) -> None:
        from claudemark.core.benchmarks import run_benchmark_suite
        res = run_benchmark_suite(reproduce=True)
        assert res.total_samples > 0
        claude_m = next(m for m in res.metrics if m.detector_name == "claude")
        assert claude_m.recall > 0.0
        assert claude_m.f1_score > 0.0

    def test_experimental_sweep_evaluates_samples(self) -> None:
        from claudemark.watermark.experimental import run_parameter_sweep
        sweep = run_parameter_sweep()
        assert len(sweep.evaluations) > 0
        assert sweep.evaluations[0].f1_score > 0.0

