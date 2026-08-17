"""Unit and integration tests for ClaudeMark v2.1.0 production-grade features."""

import tempfile
from pathlib import Path
from claudemark.core.doctor import run_doctor_diagnostics
from claudemark.core.benchmarks import run_benchmark_suite
from claudemark.provenance.audit import audit_directory
from claudemark.provenance.sarif import convert_audit_report_to_sarif, export_sarif


def test_doctor_diagnostics():
    report = run_doctor_diagnostics()
    assert report.python_version != ""
    assert len(report.items) >= 5
    assert any(it.name == "Python Version" and it.status == "OK" for it in report.items)
    assert any(it.name == "Statistical Detectors" and it.status == "OK" for it in report.items)


def test_benchmark_suite_reproducible():
    result = run_benchmark_suite(reproduce=True)
    assert result.version == "2.1.0"
    assert len(result.metrics) >= 4
    for m in result.metrics:
        assert m.accuracy >= 0.0
        assert m.f1_score >= 0.0


def test_sarif_export():
    with tempfile.TemporaryDirectory() as td:
        sample_file = Path(td) / "sample.txt"
        sample_file.write_text("Clean sample content without watermarks", encoding="utf-8")
        
        rep = audit_directory(Path(td))
        sarif_data = convert_audit_report_to_sarif(rep)
        assert sarif_data["version"] == "2.1.0"
        assert len(sarif_data["runs"]) == 1
        assert sarif_data["runs"][0]["tool"]["driver"]["name"] == "ClaudeMark"

        out_sarif = Path(td) / "results.sarif"
        export_sarif(rep, out_sarif)
        assert out_sarif.is_file()
        assert "ClaudeMark" in out_sarif.read_text(encoding="utf-8")
