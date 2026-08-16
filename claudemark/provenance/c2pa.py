"""C2PA manifest detection, extraction, and verification for ClaudeMark."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

# Magic signatures for C2PA JUMBF boxes
C2PA_JUMBF_UUID = b"\x63\x32\x70\x61"  # "c2pa"
C2PA_BOX_TYPE = b"c2pa"
C2PA_MANIFEST_URN = b"urn:c2pa:"


def inspect_c2pa_bytes(data: bytes) -> dict[str, Any]:
    """Scan raw bytes for embedded C2PA JUMBF containers and assertions."""
    has_c2pa = (
        C2PA_JUMBF_UUID in data or
        C2PA_BOX_TYPE in data or
        C2PA_MANIFEST_URN in data or
        b"c2pa.assertions" in data or
        b"c2pa.signature" in data
    )

    details: dict[str, Any] = {
        "has_c2pa": has_c2pa,
        "method": "byte_scan",
    }

    if has_c2pa:
        # Check specific indicators
        indicators = []
        if b"c2pa.assertions" in data:
            indicators.append("C2PA Assertion Manifest")
        if b"c2pa.signature" in data:
            indicators.append("Cryptographic Provenance Signature")
        if b"stds.schema-org.CreativeWork" in data:
            indicators.append("Schema.org Attribution Claims")
        details["indicators"] = indicators
    else:
        details["indicators"] = []

    return details


def inspect_c2pa_tool(file_path: Path) -> dict[str, Any] | None:
    """Use c2patool if available on the system for full cryptographic verification."""
    tool = shutil.which("c2patool")
    if not tool or not file_path.is_file():
        return None

    try:
        proc = subprocess.run(
            [tool, str(file_path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                manifest_json = json.loads(proc.stdout)
                return {
                    "has_c2pa": True,
                    "method": "c2patool",
                    "manifest": manifest_json,
                }
            except json.JSONDecodeError:
                return {
                    "has_c2pa": True,
                    "method": "c2patool_raw",
                    "output": proc.stdout[:1000],
                }
    except Exception:
        pass
    return None
