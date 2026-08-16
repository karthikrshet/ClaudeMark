"""Pixel hash and perceptual similarity utilities for image forensics."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def compute_pixel_hashes(image_path: Path) -> dict[str, str]:
    """Compute cryptographic hashes of the raw image file."""
    path = Path(image_path).resolve()
    if not path.is_file():
        return {}

    data = path.read_bytes()
    return {
        "md5": hashlib.md5(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "file_size": str(len(data)),
    }


def compare_image_hashes(original_path: Path, processed_path: Path) -> dict[str, Any]:
    """Compare hashes between original and cleaned/purified images."""
    orig_hashes = compute_pixel_hashes(original_path)
    proc_hashes = compute_pixel_hashes(processed_path)

    identical_bytes = orig_hashes.get("sha256") == proc_hashes.get("sha256")

    return {
        "original_sha256": orig_hashes.get("sha256", ""),
        "processed_sha256": proc_hashes.get("sha256", ""),
        "identical_bytes": identical_bytes,
        "size_difference_bytes": int(proc_hashes.get("file_size", 0)) - int(orig_hashes.get("file_size", 0)),
    }
