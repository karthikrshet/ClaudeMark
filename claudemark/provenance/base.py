"""Base classes and standardized schemas for ClaudeMark file provenance & cleaning."""

from __future__ import annotations

import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def validate_safe_path(p: Path | str, base_dir: Path | str | None = None) -> Path:
    """Validate and sanitize file path to prevent arbitrary path traversal and injection."""
    raw = str(p).strip()
    if "\x00" in raw:
        raise ValueError("Illegal null byte in file path")

    # Resolve symlinks and normalize to absolute path
    resolved_path = Path(raw).resolve()

    if base_dir is not None:
        resolved_base = Path(base_dir).resolve()
        try:
            resolved_path.relative_to(resolved_base)
        except ValueError:
            raise ValueError(f"Path traversal detected: {resolved_path} is outside {resolved_base}")

    return resolved_path


def safe_atomic_write_bytes(destination: Path | str, data: bytes) -> None:
    """Safely write bytes to a file via a temporary file and atomic replace."""
    safe_dest = validate_safe_path(destination)
    parent_dir = safe_dest.parent.resolve()
    parent_dir.mkdir(parents=True, exist_ok=True)

    # Remove existing symlinks to prevent symlink hijacking
    if safe_dest.is_symlink():
        safe_dest.unlink()

    # Create temporary file inside parent directory for safe atomic swap
    tmp_fd, tmp_path_str = tempfile.mkstemp(prefix=".cm_tmp_", dir=str(parent_dir))
    tmp_path = Path(tmp_path_str).resolve()
    try:
        with os.fdopen(tmp_fd, "wb") as f:
            f.write(data)
        os.replace(str(tmp_path), str(safe_dest))
    except Exception:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
        raise


def safe_atomic_write_text(destination: Path | str, text: str, encoding: str = "utf-8") -> None:
    """Safely write text to a file via atomic replacement."""
    safe_atomic_write_bytes(destination, text.encode(encoding, errors="replace"))


@dataclass
class ProvenanceInspectionReport:
    """Standardized report for file and container provenance inspection."""
    file_path: str
    file_name: str
    file_format: str
    file_size_bytes: int
    has_c2pa: bool = False
    has_exif: bool = False
    has_xmp: bool = False
    has_ai_metadata: bool = False
    suspicious: bool = False
    unicode_anomalies: int = 0
    statistical_score: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FileCleaningReport:
    """Standardized report produced when cleaning a document or image."""
    input_path: str
    output_path: str
    file_format: str
    original_size_bytes: int
    cleaned_size_bytes: int
    size_delta_bytes: int
    success: bool
    actions_performed: list[str] = field(default_factory=list)
    metadata_stripped: bool = False
    unicode_cleaned: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BatchProcessSummary:
    """Summary of batch directory inspection or cleaning."""
    directory: str
    total_files_scanned: int = 0
    supported_files_count: int = 0
    suspicious_count: int = 0
    cleaned_count: int = 0
    failed_count: int = 0
    file_reports: list[dict[str, Any]] = field(default_factory=list)

    @property
    def reports(self) -> list[dict[str, Any]]:
        return self.file_reports

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
