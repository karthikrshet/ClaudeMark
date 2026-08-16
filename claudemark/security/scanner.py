"""Defensive security scanners for archive bombs, malicious PDFs, macros, and path traversal.

Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import io
import os
import re
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Maximum safe decompression threshold (100 MB default)
MAX_SAFE_DECOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_SAFE_COMPRESSION_RATIO = 100.0

# Windows reserved device names
_RESERVED_WINDOWS_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}

# Malicious PDF action markers
_PDF_DANGEROUS_ACTIONS = [
    rb"/JavaScript", rb"/JS", rb"/Launch", rb"/EmbeddedFiles",
    rb"/SubmitForm", rb"/ImportData", rb"/GoToR", rb"/URI",
]


@dataclass
class SecurityScanReport:
    """Standardized report for file security and vulnerability analysis."""
    file_path: str
    file_name: str
    file_format: str
    is_safe: bool
    warnings: list[str] = field(default_factory=list)
    threat_level: str = "LOW"  # "NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def check_path_security(path_str: str) -> list[str]:
    """Check filename or path string for traversal, null bytes, and reserved device names."""
    warnings: list[str] = []
    if "\x00" in path_str:
        warnings.append("Illegal null byte in filename / path")
    if ".." in path_str.replace("\\", "/").split("/"):
        warnings.append("Directory traversal sequence (..) detected in path")

    base = Path(path_str).stem.upper()
    if base in _RESERVED_WINDOWS_NAMES:
        warnings.append(f"Windows reserved device name '{base}' detected")

    return warnings


def scan_file_security(file_path: Path) -> SecurityScanReport:
    """Execute defensive security inspection across document, image, or container files."""
    path = Path(file_path).resolve()
    if not path.is_file():
        return SecurityScanReport(
            file_path=str(path),
            file_name=path.name,
            file_format="unknown",
            is_safe=False,
            warnings=["File not found or inaccessible"],
            threat_level="HIGH",
        )

    name = path.name
    suffix = path.suffix.lower()
    size = path.stat().st_size
    data = path.read_bytes()

    warnings: list[str] = check_path_security(name)
    details: dict[str, Any] = {"file_size_bytes": size}

    # 1. Archive bomb and macro inspection for zip-based containers (DOCX, ODT, ZIP)
    if suffix in (".docx", ".odt", ".zip", ".jar"):
        try:
            with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
                total_uncompressed = 0
                has_macros = False
                external_targets: list[str] = []

                for info in zf.infolist():
                    # Path traversal inside zip entries
                    if ".." in info.filename or info.filename.startswith(("/", "\\")):
                        warnings.append(f"Unsafe zip entry path: '{info.filename}'")

                    total_uncompressed += info.file_size
                    # Check for VBA macros
                    if "vbaProject.bin" in info.filename or info.filename.endswith((".vba", ".bas", ".cls")):
                        has_macros = True

                    # Inspect relationship files for external SSRF / remote targets
                    if info.filename.endswith(".rels"):
                        try:
                            rel_content = zf.read(info.filename).decode("utf-8", errors="replace")
                            for match in re.finditer(r'Target="([^"]+)"\s+TargetMode="External"', rel_content):
                                external_targets.append(match.group(1))
                        except Exception:
                            pass

                # Calculate compression ratio
                ratio = (total_uncompressed / size) if size > 0 else 0.0
                details["uncompressed_size_bytes"] = total_uncompressed
                details["compression_ratio"] = round(ratio, 2)
                details["external_relationship_targets"] = external_targets

                if ratio > MAX_SAFE_COMPRESSION_RATIO or total_uncompressed > MAX_SAFE_DECOMPRESSED_BYTES:
                    warnings.append(f"Potential zip bomb: compression ratio {ratio:.1f}x (uncompressed: {total_uncompressed / 1024 / 1024:.1f} MB)")

                if has_macros:
                    warnings.append("Embedded executable VBA macros detected (macro payload)")

                if external_targets:
                    warnings.append(f"External document relationships detected: {len(external_targets)} external link(s)")

        except zipfile.BadZipFile:
            warnings.append("Malformed or corrupted ZIP container structure")
        except Exception as ex:
            warnings.append(f"Error scanning archive: {str(ex)}")

    # 2. PDF Security inspection
    elif suffix == ".pdf":
        found_actions = []
        for action in _PDF_DANGEROUS_ACTIONS:
            if action in data:
                found_actions.append(action.decode("ascii", errors="replace"))

        details["suspicious_pdf_actions"] = found_actions
        if found_actions:
            warnings.append(f"Suspicious executable PDF actions detected: {', '.join(found_actions)}")

    threat_level = "NONE"
    if warnings:
        threat_level = "CRITICAL" if any("bomb" in w or "VBA" in w for w in warnings) else "HIGH"

    return SecurityScanReport(
        file_path=str(path),
        file_name=name,
        file_format=suffix.lstrip("."),
        is_safe=len(warnings) == 0,
        warnings=warnings,
        threat_level=threat_level,
        details=details,
    )
