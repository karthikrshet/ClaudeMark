"""Tests for defensive security scanner (zip bomb protection, PDF actions, Windows reserved names)."""

import io
import zipfile
import pytest
from claudemark.security.scanner import check_path_security, scan_file_security


def test_path_security_checks():
    assert len(check_path_security("safe_document.pdf")) == 0
    assert len(check_path_security("test\x00null.txt")) > 0
    assert len(check_path_security("../../../etc/passwd")) > 0
    assert len(check_path_security("CON.txt")) > 0
    assert len(check_path_security("NUL.docx")) > 0


def test_scan_clean_pdf(tmp_path):
    pdf = tmp_path / "clean.pdf"
    pdf.write_bytes(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF")
    rep = scan_file_security(pdf)
    assert rep.is_safe is True
    assert rep.threat_level == "NONE"


def test_scan_malicious_pdf(tmp_path):
    pdf = tmp_path / "exploit.pdf"
    pdf.write_bytes(b"%PDF-1.4\n/JavaScript (app.alert('evil')) /Launch /EmbeddedFiles")
    rep = scan_file_security(pdf)
    assert rep.is_safe is False
    assert any("JavaScript" in w for w in rep.warnings)


def test_scan_docx_with_macro(tmp_path):
    docx = tmp_path / "sample.docx"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("word/vbaProject.bin", b"VBA MACRO PAYLOAD")
    docx.write_bytes(buf.getvalue())

    rep = scan_file_security(docx)
    assert rep.is_safe is False
    assert any("VBA" in w for w in rep.warnings)
