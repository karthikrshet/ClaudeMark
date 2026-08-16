"""Multimedia (MP4, MOV, MP3, M4A) provenance inspection and metadata stripping.

Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import os
import struct
from pathlib import Path
from typing import Any

from .base import (
    FileCleaningReport,
    ProvenanceInspectionReport,
    safe_atomic_write_bytes,
    validate_safe_path,
)


def inspect_multimedia_file(file_path: Path | str) -> ProvenanceInspectionReport:
    """Inspect multimedia container (MP4, MOV, MP3, M4A) for metadata atoms and tags."""
    safe_path = validate_safe_path(file_path)
    suffix = safe_path.suffix.lower()
    data = safe_path.read_bytes()
    size = len(data)

    has_metadata = False
    details: dict[str, Any] = {"format": suffix.lstrip(".")}

    if suffix in (".mp4", ".mov", ".m4a"):
        pos = 0
        boxes_found: list[str] = []
        while pos + 8 <= len(data):
            box_len = struct.unpack(">I", data[pos:pos+4])[0]
            box_type = data[pos+4:pos+8]
            if box_len == 1 and pos + 16 <= len(data):
                box_len = struct.unpack(">Q", data[pos+8:pos+16])[0]
            elif box_len == 0:
                box_len = len(data) - pos

            if box_len <= 0 or pos + box_len > len(data):
                break

            name = box_type.decode("latin1", errors="replace")
            if box_type in (b"udta", b"meta", b"c2pa", b"uuid", b"XMP_"):
                has_metadata = True
                boxes_found.append(name)
            pos += box_len

        details["metadata_boxes"] = boxes_found

    elif suffix == ".mp3":
        has_id3v2 = data[:3] == b"ID3"
        has_id3v1 = len(data) >= 128 and data[-128:-125] == b"TAG"
        has_metadata = has_id3v2 or has_id3v1
        details["has_id3v2"] = has_id3v2
        details["has_id3v1"] = has_id3v1

    return ProvenanceInspectionReport(
        file_path=str(safe_path),
        file_name=safe_path.name,
        file_format=suffix.lstrip("."),
        file_size_bytes=size,
        suspicious=has_metadata,
        has_c2pa="c2pa" in details.get("metadata_boxes", []),
        has_exif=False,
        has_xmp="XMP_" in details.get("metadata_boxes", []),
        has_ai_metadata=has_metadata,
        details=details,
        summary=f"Multimedia ({suffix.lstrip('.').upper()}): {'Metadata atoms / tags present' if has_metadata else 'Clean container'}",
    )


def clean_multimedia_file(
    input_path: Path | str,
    output_path: Path | str | None = None,
) -> FileCleaningReport:
    """Strip metadata atoms and ID3 tags from multimedia files atomically."""
    safe_in = validate_safe_path(input_path)
    safe_out = validate_safe_path(output_path) if output_path else safe_in

    suffix = safe_in.suffix.lower()
    data = safe_in.read_bytes()
    orig_size = len(data)
    actions: list[str] = []
    cleaned_payload = data

    if suffix in (".mp4", ".mov", ".m4a"):
        pos = 0
        retained: list[bytes] = []
        while pos + 8 <= len(data):
            box_len = struct.unpack(">I", data[pos:pos+4])[0]
            box_type = data[pos+4:pos+8]
            if box_len == 1 and pos + 16 <= len(data):
                box_len = struct.unpack(">Q", data[pos+8:pos+16])[0]
            elif box_len == 0:
                box_len = len(data) - pos

            if box_len <= 0 or pos + box_len > len(data):
                retained.append(data[pos:])
                break

            box_data = data[pos:pos+box_len]
            pos += box_len

            if box_type in (b"udta", b"c2pa", b"uuid", b"XMP_"):
                actions.append(f"Stripped multimedia atom: {box_type.decode('latin1', errors='replace')}")
                continue
            retained.append(box_data)

        cleaned_payload = b"".join(retained)
        safe_atomic_write_bytes(safe_out, cleaned_payload)

    elif suffix == ".mp3":
        pos = 0
        # Strip ID3v2 tag
        if data[:3] == b"ID3" and len(data) >= 10:
            tag_size = (
                ((data[6] & 0x7F) << 21)
                | ((data[7] & 0x7F) << 14)
                | ((data[8] & 0x7F) << 7)
                | (data[9] & 0x7F)
            )
            pos = 10 + tag_size
            actions.append("Stripped ID3v2 metadata header")

        end_pos = len(data)
        # Strip ID3v1 tag
        if len(data) >= 128 and data[-128:-125] == b"TAG":
            end_pos -= 128
            actions.append("Stripped ID3v1 metadata trailer")

        cleaned_payload = data[pos:end_pos]
        safe_atomic_write_bytes(safe_out, cleaned_payload)

    else:
        safe_atomic_write_bytes(safe_out, data)

    new_size = len(cleaned_payload)

    return FileCleaningReport(
        input_path=str(safe_in),
        output_path=str(safe_out),
        file_format=suffix.lstrip("."),
        original_size_bytes=orig_size,
        cleaned_size_bytes=new_size,
        size_delta_bytes=new_size - orig_size,
        success=True,
        actions_performed=actions or ["Sanitized multimedia container structure"],
        metadata_stripped=bool(actions),
    )
