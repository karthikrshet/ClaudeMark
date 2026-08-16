"""Base classes and standardized schemas for ClaudeMark file provenance & cleaning."""

from __future__ import annotations

import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def validate_safe_path(p: Path | str, base_dir: Path | str | None = None) -> Path:
    """Validate and sanitize file path to prevent arbitrary path traversal and injection."""
    path_obj = Path(p).resolve()
    raw = str(path_obj)
    if "\x00" in raw:
        raise ValueError("Illegal null byte in file path")
    if base_dir is not None:
        base_path = Path(base_dir).resolve()
        try:
            path_obj.relative_to(base_path)
        except ValueError:
            raise ValueError(f"Path traversal detected: {path_obj} is outside {base_path}")
    return path_obj


def safe_atomic_write_bytes(destination: Path, data: bytes) -> None:
    """Safely write bytes to a file via a temporary file and atomic replace to prevent symlink hijacking and partial writes."""
    dest = Path(destination).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Prevent symlink redirection
    if dest.is_symlink():
        dest.unlink()

    # Write to temp file in same directory to guarantee same filesystem for atomic rename
    tmp_fd, tmp_path = tempfile.mkstemp(prefix=".cm_tmp_", dir=str(dest.parent))
    try:
        with os.fdopen(tmp_fd, "wb") as f:
            f.write(data)
        os.replace(tmp_path, str(dest))
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        raise


def safe_atomic_write_text(destination: Path, text: str, encoding: str = "utf-8") -> None:
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
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BatchProcessSummary:
    """Summary of batch directory inspection or cleaning."""
    directory: str
    total_files_scanned: int
    supported_files_count: int
    suspicious_count: int = 0
    cleaned_count: int = 0
    failed_count: int = 0
    file_reports: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
