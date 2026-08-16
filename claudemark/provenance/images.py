"""Self-contained image provenance inspection and metadata stripping for ClaudeMark.

Supports: PNG, JPEG, WebP, SVG, AVIF, and HEIC.
Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import io
import re
import struct
import zlib
from pathlib import Path
from typing import Any

from .base import (
    FileCleaningReport,
    ProvenanceInspectionReport,
    safe_atomic_write_bytes,
    safe_atomic_write_text,
    validate_safe_path,
)
from .c2pa import inspect_c2pa_bytes
from .exif_xmp import inspect_exif_xmp_bytes

# PNG chunk signatures to strip
PNG_METADATA_CHUNKS = {b"tEXt", b"zTXt", b"iTXt", b"eXIf", b"c2pa", b"dSIG"}

# JPEG markers
JPEG_APP1 = 0xE1   # EXIF / XMP
JPEG_APP13 = 0xED  # IPTC / Photoshop
JPEG_COM = 0xFE    # Comment

# SVG metadata regex
_SVG_METADATA_RE = re.compile(r"<metadata.*?</metadata>", re.DOTALL | re.IGNORECASE)
_SVG_COMMENTS_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def inspect_image_file(file_path: Path) -> ProvenanceInspectionReport:
    """Inspect image file for EXIF, XMP, C2PA, and AI-generator markers."""
    file_path = validate_safe_path(file_path)
    suffix = file_path.suffix.lower()
    size = file_path.stat().st_size
    data = file_path.read_bytes()

    c2pa_info = inspect_c2pa_bytes(data)
    meta_info = inspect_exif_xmp_bytes(data)

    has_c2pa = c2pa_info["has_c2pa"]
    has_exif = meta_info["has_exif"]
    has_xmp = meta_info["has_xmp"]
    has_ai = meta_info["has_ai_metadata"]
    suspicious = has_c2pa or has_exif or has_xmp or has_ai

    details = {
        "c2pa": c2pa_info,
        "metadata": meta_info,
    }

    return ProvenanceInspectionReport(
        file_path=str(file_path),
        file_name=file_path.name,
        file_format=suffix.lstrip("."),
        file_size_bytes=size,
        has_c2pa=has_c2pa,
        has_exif=has_exif,
        has_xmp=has_xmp,
        has_ai_metadata=has_ai,
        suspicious=suspicious,
        details=details,
        summary=f"Image ({suffix.lstrip('.').upper()}): {'AI provenance metadata found' if suspicious else 'Clean image metadata'}",
    )


def clean_image_file(
    input_path: Path,
    output_path: Path | None = None,
    strip_all: bool = True,
    remove_pixel: str | None = None,
) -> FileCleaningReport:
    """Strip metadata chunks from image containers safely."""
    input_path = validate_safe_path(input_path)
    suffix = input_path.suffix.lower()
    out = validate_safe_path(output_path) if output_path else input_path
    orig_size = input_path.stat().st_size
    data = input_path.read_bytes()
    actions: list[str] = []

    if suffix == ".png":
        # Process PNG chunk stream
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            out_buf = bytearray(data[:8])
            pos = 8
            while pos < len(data):
                if pos + 8 > len(data):
                    break
                length = struct.unpack(">I", data[pos:pos+4])[0]
                chunk_type = data[pos+4:pos+8]
                chunk_total_len = 12 + length
                chunk_data = data[pos:pos+chunk_total_len]
                pos += chunk_total_len

                if chunk_type in PNG_METADATA_CHUNKS:
                    actions.append(f"Stripped PNG chunk: {chunk_type.decode('latin1')}")
                    continue
                out_buf.extend(chunk_data)
            safe_atomic_write_bytes(out, bytes(out_buf))
        else:
            safe_atomic_write_bytes(out, data)

    elif suffix in (".jpg", ".jpeg"):
        # Process JPEG segment stream
        if data[:2] == b"\xff\xd8":
            out_buf = bytearray(b"\xff\xd8")
            pos = 2
            while pos < len(data):
                if data[pos] != 0xFF:
                    out_buf.extend(data[pos:])
                    break
                marker = data[pos+1]
                if marker in (0xD9, 0xDA):  # SOS or EOI
                    out_buf.extend(data[pos:])
                    break
                if marker in (0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0x00):
                    out_buf.extend(data[pos:pos+2])
                    pos += 2
                    continue
                seg_len = struct.unpack(">H", data[pos+2:pos+4])[0]
                if marker in (JPEG_APP1, JPEG_APP13, JPEG_COM):
                    actions.append(f"Stripped JPEG marker: 0x{marker:02X}")
                    pos += 2 + seg_len
                    continue
                out_buf.extend(data[pos:pos+2+seg_len])
                pos += 2 + seg_len
            safe_atomic_write_bytes(out, bytes(out_buf))
        else:
            safe_atomic_write_bytes(out, data)

    elif suffix == ".webp":
        # Process WebP RIFF chunks
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            pos = 12
            chunks: list[bytes] = []
            while pos < len(data):
                if pos + 8 > len(data):
                    break
                fourcc = data[pos:pos+4]
                size = struct.unpack("<I", data[pos+4:pos+8])[0]
                pad = size % 2
                chunk_total = 8 + size + pad
                chunk_bytes = data[pos:pos+chunk_total]
                pos += chunk_total

                if fourcc in (b"EXIF", b"XMP ", b"C2PA", b"ICCP"):
                    actions.append(f"Stripped WebP chunk: {fourcc.decode('latin1')}")
                    continue
                chunks.append(chunk_bytes)

            payload = b"".join(chunks)
            header = b"RIFF" + struct.pack("<I", 4 + len(payload)) + b"WEBP"
            safe_atomic_write_bytes(out, header + payload)
        else:
            safe_atomic_write_bytes(out, data)

    elif suffix in (".avif", ".heic", ".heif"):
        # Process ISOBMFF box streams (AVIF / HEIC)
        if len(data) >= 8:
            pos = 0
            boxes: list[tuple[bytes, bytes]] = []  # (box_type, box_bytes)
            while pos < len(data):
                if pos + 8 > len(data):
                    break
                box_len = struct.unpack(">I", data[pos:pos+4])[0]
                box_type = data[pos+4:pos+8]
                if box_len == 1:
                    # Extended 64-bit length
                    if pos + 16 > len(data):
                        break
                    box_len = struct.unpack(">Q", data[pos+8:pos+16])[0]
                elif box_len == 0:
                    # Extends to end of file
                    box_len = len(data) - pos

                if box_len <= 0 or pos + box_len > len(data):
                    break

                box_bytes = data[pos:pos+box_len]
                pos += box_len

                # Strip standalone top-level c2pa, Exif, or xml boxes
                if box_type in (b"c2pa", b"Exif", b"xml ", b"uuid"):
                    actions.append(f"Stripped ISOBMFF box: {box_type.decode('latin1', errors='replace')}")
                    continue
                boxes.append((box_type, box_bytes))

            if boxes:
                payload = b"".join(b[1] for b in boxes)
                safe_atomic_write_bytes(out, payload)
            else:
                safe_atomic_write_bytes(out, data)
        else:
            safe_atomic_write_bytes(out, data)

    elif suffix == ".svg":
        raw_svg = data.decode("utf-8", errors="replace")
        clean_svg = _SVG_METADATA_RE.sub("", raw_svg)
        clean_svg = _SVG_COMMENTS_RE.sub("", clean_svg)
        safe_atomic_write_text(out, clean_svg, encoding="utf-8")
        actions.append("Stripped SVG <metadata> and XML comments")

    else:
        safe_atomic_write_bytes(out, data)

    new_size = out.stat().st_size if out.is_file() else orig_size

    return FileCleaningReport(
        input_path=str(input_path),
        output_path=str(out),
        file_format=suffix.lstrip("."),
        original_size_bytes=orig_size,
        cleaned_size_bytes=new_size,
        size_delta_bytes=new_size - orig_size,
        success=True,
        actions_performed=actions or ["Sanitized image structure"],
        metadata_stripped=True,
    )
