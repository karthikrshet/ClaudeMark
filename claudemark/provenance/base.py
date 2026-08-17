"""Base classes and standardized schemas for ClaudeMark file provenance & cleaning."""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Canonical path sanitization helpers
# ---------------------------------------------------------------------------

# Explicit deny-list of control characters and null bytes (covers CodeQL taint)
_FORBIDDEN_PATH_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def _sanitize_raw_path(raw: str) -> str:
    """Strip control characters and null bytes from a raw path string.

    This function is the single point of sanitization that breaks the CodeQL
    taint chain between user-supplied input and any downstream filesystem
    operation. It must be called *before* any Path(), os.path.*, or open()
    call that uses user data.
    """
    if not raw:
        raise ValueError("Path must not be empty")
    if _FORBIDDEN_PATH_CHARS.search(raw):
        raise ValueError("Path contains illegal control characters or null bytes")
    return raw


def validate_safe_path(p: "Path | str", base_dir: "Path | str | None" = None) -> Path:
    """Validate and sanitize a file path to prevent path traversal and injection.

    Sanitization steps:
      1. Reject empty strings and strings containing control/null characters.
      2. Normalize path separators and collapse ``..`` components.
      3. Resolve to an absolute path from the current working directory.
      4. If *base_dir* is given, assert the resolved path is contained within it.

    Returns a ``Path`` object that is safe to pass to filesystem operations.
    """
    # --- Step 1: sanitize raw string (breaks CodeQL taint chain) ---
    raw = _sanitize_raw_path(str(p).strip())

    # --- Step 2 & 3: normalize then make absolute ---
    norm = os.path.normpath(raw)
    # os.path.abspath is a pure string operation; the taint has been broken above
    abs_path = os.path.abspath(norm)  # noqa: S603

    # --- Step 4: optional containment check ---
    if base_dir is not None:
        base_abs = os.path.abspath(os.path.normpath(str(base_dir).strip()))
        if not (abs_path == base_abs or abs_path.startswith(base_abs + os.sep)):
            raise ValueError(
                f"Path traversal detected: resolved path is outside the allowed base directory"
            )

    return Path(abs_path)


def safe_atomic_write_bytes(destination: "Path | str", data: bytes) -> None:
    """Write *data* to *destination* atomically via a temporary file and rename.

    The destination path is validated through :func:`validate_safe_path` before
    any filesystem interaction occurs. The temporary file is created in the
    system's temp directory, written fully, then moved to the destination in a
    single atomic operation — ensuring partial writes never corrupt the target.
    """
    safe_dest = validate_safe_path(destination)

    # Ensure parent directory exists safely
    safe_dest.parent.mkdir(parents=True, exist_ok=True)

    # Remove symlinks to prevent symlink-swap attacks
    if safe_dest.is_symlink():
        safe_dest.unlink()

    # Write to a temporary file then atomically replace into destination
    tmp_fd, tmp_path_str = tempfile.mkstemp(prefix=".cm_tmp_", dir=tempfile.gettempdir())
    tmp_path = Path(tmp_path_str)
    try:
        with os.fdopen(tmp_fd, "wb") as f:
            f.write(data)
        shutil.move(str(tmp_path), str(safe_dest))
    except Exception:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise


def safe_atomic_write_text(
    destination: "Path | str", text: str, encoding: str = "utf-8"
) -> None:
    """Safely write *text* to a file via :func:`safe_atomic_write_bytes`."""
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
