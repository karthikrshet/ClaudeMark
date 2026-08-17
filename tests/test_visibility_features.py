"""Tests for visibility, heatmap, certificate export, and packaging integrations."""

import tempfile
from pathlib import Path
from claudemark import analyze_text
from claudemark.core.text_stats import compute_sentence_heatmap
from claudemark.provenance.certificate import generate_html_certificate, save_audit_certificate


def test_compute_sentence_heatmap():
    text = "First clean sentence here. Second sentence with \u200bhidden zero-width token. Third sentence."
    heatmap = compute_sentence_heatmap(text)
    assert len(heatmap) == 3
    assert heatmap[0]["level"] in ("clean", "medium", "high")
    assert heatmap[1]["unicode_anomalies"] >= 1
    assert heatmap[1]["level"] == "high"


def test_analyze_text_includes_heatmap():
    res = analyze_text("This is a simple test sentence for analysis.")
    assert "sentence_heatmap" in res
    assert isinstance(res["sentence_heatmap"], list)
    assert len(res["sentence_heatmap"]) >= 1


def test_generate_html_certificate():
    data_bytes = b"Hello forensic test document."
    report_data = {
        "suspicious": False,
        "total_unicode_anomalies": 0,
        "total_c2pa_manifests": 0,
    }
    html = generate_html_certificate("test.txt", data_bytes, report_data)
    assert "<!DOCTYPE html>" in html
    assert "Claude" in html
    assert "VERIFIED CLEAN" in html
    assert "SHA-256 Content Digest" in html


def test_save_audit_certificate():
    with tempfile.TemporaryDirectory() as td:
        src_file = Path(td) / "sample.txt"
        src_file.write_text("Audit test file content", encoding="utf-8")
        out_cert = Path(td) / "certificate.html"

        res_path = save_audit_certificate(src_file, {"suspicious": False}, out_cert)
        assert res_path.is_file()
        content = res_path.read_text(encoding="utf-8")
        assert "sample.txt" in content
        assert "Claude" in content
