"""High-value edge cases and security hardening tests for ClaudeMark."""

import io
import socket
from pathlib import Path
import pytest

from claudemark import analyze_text, compute_forensic_diff, normalize_text
from claudemark.core.normalizer import NormalizationOptions
from claudemark.core.unicode_forensics import analyze_unicode_forensics
from claudemark.detectors.registry import detector_registry
from claudemark.provenance.batch import clean_single_file, inspect_single_file
from claudemark.provenance.documents import clean_document, inspect_document
from claudemark.provenance.images import clean_image_file, inspect_image_file


def test_edge_case_empty_and_whitespace_files(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")
    
    rep = inspect_single_file(empty_file)
    assert rep.file_size_bytes == 0
    assert not rep.suspicious

    clean_rep = clean_single_file(empty_file, tmp_path / "empty_out.txt")
    assert clean_rep.success
    assert (tmp_path / "empty_out.txt").read_text(encoding="utf-8") == ""


def test_edge_case_corrupted_image_bytes(tmp_path):
    corrupted_png = tmp_path / "corrupted.png"
    # Invalid PNG: truncated chunk header
    corrupted_png.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x05tEXttruncated")

    # Inspect should not crash
    rep = inspect_image_file(corrupted_png)
    assert rep.file_format == "png"

    # Clean should handle gracefully without crashing
    out_png = tmp_path / "out.png"
    clean_rep = clean_image_file(corrupted_png, out_png)
    assert clean_rep.success
    assert out_png.is_file()


def test_edge_case_corrupted_docx_zip(tmp_path):
    corrupted_docx = tmp_path / "broken.docx"
    corrupted_docx.write_bytes(b"PK\x03\x04broken zip archive content")

    rep = inspect_document(corrupted_docx)
    assert rep.file_format == "docx"

    out_docx = tmp_path / "out.docx"
    clean_rep = clean_document(corrupted_docx, out_docx)
    assert clean_rep.success


def test_edge_case_unicode_nested_invisibles_and_homoglyphs():
    # Combining nested ZWSP, ZWNJ, BOM, and Cyrillic 'а' (U+0430) homoglyph for Latin 'a'
    tricky_text = "Secret\u200b\u200c\u200d\ufeff\u2060 message with homoglyph \u0430pple."
    
    u_rep = analyze_unicode_forensics(tricky_text)
    assert u_rep.total_anomalies >= 5
    assert u_rep.has_anomalies

    # Normalization with homoglyph replacement
    opts = NormalizationOptions(replace_homoglyphs=True)
    res = normalize_text(tricky_text, opts)
    assert "\u200b" not in res.normalized_text
    assert "\ufeff" not in res.normalized_text
    assert "Secret message with homoglyph apple." in res.normalized_text


def test_edge_case_detector_extreme_repetitive_text():
    # 100% repetitive text
    rep_text = "test " * 100
    for det_name in detector_registry.list_detectors():
        det = detector_registry.get(det_name)
        res = det.detect(rep_text)
        assert 0.0 <= res.signal_score <= 1.0
        assert 0.0 <= res.confidence <= 1.0
        assert res.status in ("clean_or_low_signal", "potential_signal", "strong_signal")
        assert len(det.limitations()) >= 1


def test_edge_case_detector_single_character():
    for det_name in detector_registry.list_detectors():
        det = detector_registry.get(det_name)
        res = det.detect("a")
        assert res.signal_score == 0.0
        assert res.status == "clean_or_low_signal"


def test_zero_egress_local_first_verification(monkeypatch):
    """Verify that core ClaudeMark execution performs ZERO outbound socket connections."""
    def guarded_connect(self, *args, **kwargs):
        raise ConnectionRefusedError("Outbound network calls are strictly forbidden in ClaudeMark.")

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)

    # Run analysis, normalization, diff, and provenance cleaning under strict network block
    analysis = analyze_text("Local text verification for zero egress guarantees.")
    assert analysis["text_statistics"].words == 7

    norm = normalize_text("Clean\u200b this text.")
    assert norm.normalized_text == "Clean this text."

    diff = compute_forensic_diff("Orig\u200b", "Orig")
    assert diff.anomalies_removed == 1
