"""Tests for AVIF/HEIC ISOBMFF stripping, directory auditing, and skill installation."""

import struct
from pathlib import Path
from claudemark.provenance.images import clean_image_file, inspect_image_file
from claudemark.provenance.audit import audit_directory
from install_skill import install_skill


def test_isobmff_avif_cleaning(tmp_path):
    # Construct a synthetic ISOBMFF AVIF container with ftyp, meta, c2pa box
    ftyp_data = b"avif\x00\x00\x00\x00mif1miaf"
    ftyp_box = struct.pack(">I", 8 + len(ftyp_data)) + b"ftyp" + ftyp_data

    c2pa_data = b"C2PA Claim Data"
    c2pa_box = struct.pack(">I", 8 + len(c2pa_data)) + b"c2pa" + c2pa_data

    mdat_data = b"\x00" * 32
    mdat_box = struct.pack(">I", 8 + len(mdat_data)) + b"mdat" + mdat_data

    raw_avif = ftyp_box + c2pa_box + mdat_box
    input_file = tmp_path / "sample.avif"
    input_file.write_bytes(raw_avif)

    out_file = tmp_path / "cleaned.avif"
    rep = clean_image_file(input_file, out_file)
    assert rep.success is True
    assert out_file.is_file()
    cleaned_bytes = out_file.read_bytes()
    assert b"c2pa" not in cleaned_bytes
    assert b"avif" in cleaned_bytes
    assert b"mdat" in cleaned_bytes


def test_directory_audit(tmp_path):
    # Create sample files in a directory tree
    sub = tmp_path / "subdir"
    sub.mkdir()

    f1 = tmp_path / "text.txt"
    f1.write_text("Hello\u200bWorld with hidden space", encoding="utf-8")

    f2 = sub / "doc.md"
    f2.write_text("# Clean Document\nNo anomalies.", encoding="utf-8")

    rep = audit_directory(tmp_path)
    assert rep.total_files_scanned == 2
    assert rep.total_unicode_anomalies == 1
    assert rep.total_suspicious_files == 1
    assert len(rep.findings) >= 1
    assert rep.findings[0].confidence == "confirmed"


def test_skill_installer(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    ret = install_skill(force=True, target_env="cursor")
    assert ret == 0
    installed_skill = tmp_path / ".cursor" / "skills" / "ai-forensics" / "SKILL.md"
    assert installed_skill.is_file()
