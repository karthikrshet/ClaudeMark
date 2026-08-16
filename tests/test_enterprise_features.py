"""Tests for universal agent installations, multimedia cleaning, HTML diff, and schema export."""

import struct
from pathlib import Path
from claudemark.provenance.multimedia import inspect_multimedia_file, clean_multimedia_file
from claudemark.core.diff import compute_forensic_diff, render_html_diff
from claudemark.cli import main
from install_skill import install_skill


def test_multimedia_mp4_cleaning(tmp_path):
    # Construct a synthetic ISOBMFF MP4 container with ftyp, udta (metadata), and mdat (media)
    ftyp_data = b"isom\x00\x00\x02\x00isomiso2mp41"
    ftyp_box = struct.pack(">I", 8 + len(ftyp_data)) + b"ftyp" + ftyp_data

    udta_data = b"Creator AI Tag: Antigravity Forensics"
    udta_box = struct.pack(">I", 8 + len(udta_data)) + b"udta" + udta_data

    mdat_data = b"\x00\x00\x01\xba" + b"\x00" * 64
    mdat_box = struct.pack(">I", 8 + len(mdat_data)) + b"mdat" + mdat_data

    raw_mp4 = ftyp_box + udta_box + mdat_box
    input_file = tmp_path / "video.mp4"
    input_file.write_bytes(raw_mp4)

    insp = inspect_multimedia_file(input_file)
    assert insp.suspicious is True
    assert "udta" in insp.details.get("metadata_boxes", [])

    out_file = tmp_path / "clean_video.mp4"
    rep = clean_multimedia_file(input_file, out_file)
    assert rep.success is True
    assert out_file.is_file()
    cleaned_bytes = out_file.read_bytes()
    assert b"udta" not in cleaned_bytes
    assert b"ftyp" in cleaned_bytes
    assert b"mdat" in cleaned_bytes


def test_multimedia_mp3_cleaning(tmp_path):
    # Construct a synthetic MP3 file with ID3v2 header and audio payload
    id3_header = b"ID3\x04\x00\x00\x00\x00\x00\x10" + b"\x00" * 16
    audio_frames = b"\xff\xfb\x90\x64" * 16
    id3_trailer = b"TAG" + b"A" * 125  # 128-byte ID3v1 trailer

    raw_mp3 = id3_header + audio_frames + id3_trailer
    input_file = tmp_path / "audio.mp3"
    input_file.write_bytes(raw_mp3)

    insp = inspect_multimedia_file(input_file)
    assert insp.suspicious is True
    assert insp.details["has_id3v2"] is True
    assert insp.details["has_id3v1"] is True

    out_file = tmp_path / "clean_audio.mp3"
    rep = clean_multimedia_file(input_file, out_file)
    assert rep.success is True
    cleaned_bytes = out_file.read_bytes()
    assert not cleaned_bytes.startswith(b"ID3")
    assert not cleaned_bytes.endswith(b"TAG" + b"A" * 125)


def test_render_html_diff():
    text1 = "Original text before transformation."
    text2 = "Transformed text after forensic sanitization."
    diff_res = compute_forensic_diff(text1, text2)
    html_out = render_html_diff(text1, text2, "text1.txt", "text2.txt", diff_res)
    assert "<!DOCTYPE html>" in html_out
    assert "ClaudeMark Forensic Comparison Report" in html_out
    assert "text1.txt" in html_out
    assert "text2.txt" in html_out


def test_universal_skill_installer(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    ret = install_skill(force=True, target_env="all")
    assert ret == 0
    assert (tmp_path / ".cursor" / "skills" / "ai-forensics" / "SKILL.md").is_file()
    assert (tmp_path / ".agents" / "skills" / "ai-forensics" / "SKILL.md").is_file()
    assert (tmp_path / ".claude" / "skills" / "ai-forensics" / "SKILL.md").is_file()
    assert (tmp_path / ".grok" / "skills" / "ai-forensics" / "SKILL.md").is_file()


def test_cli_schema(capsys):
    ret = main(["schema"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "ClaudeMarkForensicsSchema" in captured.out
    assert "analyze_watermark" in captured.out
