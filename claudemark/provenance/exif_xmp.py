"""EXIF, XMP, IPTC, and AI-generator metadata inspection."""

from __future__ import annotations

import re
from typing import Any

# AI Generator signatures in XMP / EXIF text streams
AI_METADATA_MARKERS = [
    b"midjourney",
    b"stable diffusion",
    b"dall-e",
    b"firefly",
    b"bing image creator",
    b"chatgpt",
    b"claude",
    b"adobe firefly",
    b"comfyui",
    b"automatic1111",
    b"novelai",
]


def inspect_exif_xmp_bytes(data: bytes) -> dict[str, Any]:
    """Inspect binary file content for embedded EXIF, XMP, and known AI provenance markers."""
    has_exif = b"Exif\x00\x00" in data or b"http://ns.adobe.com/exif/" in data
    has_xmp = b"http://ns.adobe.com/xap/1.0/" in data or b"<x:xmpmeta" in data or b"<?xpacket" in data
    has_iptc = b"\x1c\x02" in data

    detected_ai_markers: list[str] = []
    lower_data = data.lower()
    for marker in AI_METADATA_MARKERS:
        if marker in lower_data:
            detected_ai_markers.append(marker.decode("ascii", errors="replace"))

    return {
        "has_exif": has_exif,
        "has_xmp": has_xmp,
        "has_iptc": has_iptc,
        "has_ai_metadata": len(detected_ai_markers) > 0,
        "ai_markers": detected_ai_markers,
    }
