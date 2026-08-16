"""Batch processing engine for recursive directory inspection and cleaning."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .base import BatchProcessSummary, FileCleaningReport, ProvenanceInspectionReport
from .documents import clean_document, inspect_document
from .images import clean_image_file, inspect_image_file
from .multimedia import clean_multimedia_file, inspect_multimedia_file

SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".avif", ".heic", ".heif"}
SUPPORTED_DOC_EXTS = {".pdf", ".docx", ".odt", ".html", ".htm", ".md", ".txt", ".text"}
SUPPORTED_MEDIA_EXTS = {".mp4", ".mov", ".m4a", ".mp3"}
ALL_SUPPORTED_EXTS = SUPPORTED_IMAGE_EXTS | SUPPORTED_DOC_EXTS | SUPPORTED_MEDIA_EXTS


def inspect_single_file(file_path: Path) -> ProvenanceInspectionReport:
    """Auto-route inspection based on file extension."""
    suffix = file_path.suffix.lower()
    if suffix in SUPPORTED_IMAGE_EXTS:
        return inspect_image_file(file_path)
    elif suffix in SUPPORTED_MEDIA_EXTS:
        return inspect_multimedia_file(file_path)
    elif suffix in SUPPORTED_DOC_EXTS:
        return inspect_document(file_path)
    else:
        # Fallback to document text/container scan
        return inspect_document(file_path)


def clean_single_file(
    input_path: Path,
    output_path: Path | None = None,
    strip_all_metadata: bool = True,
    remove_pixel: str | None = None,
) -> FileCleaningReport:
    """Auto-route cleaning based on file extension."""
    suffix = input_path.suffix.lower()
    if suffix in SUPPORTED_IMAGE_EXTS:
        return clean_image_file(
            input_path,
            output_path,
            strip_all=strip_all_metadata,
            remove_pixel=remove_pixel,
        )
    elif suffix in SUPPORTED_MEDIA_EXTS:
        return clean_multimedia_file(input_path, output_path)
    else:
        return clean_document(input_path, output_path)


def batch_inspect(dir_path: Path, recursive: bool = True) -> BatchProcessSummary:
    """Inspect all supported files within a directory tree."""
    dir_path = Path(dir_path).resolve()
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path}")

    total_scanned = 0
    supported_count = 0
    suspicious_count = 0
    reports: list[dict[str, Any]] = []

    pattern = "**/*" if recursive else "*"
    for item in dir_path.glob(pattern):
        if item.is_file():
            total_scanned += 1
            if item.suffix.lower() in ALL_SUPPORTED_EXTS:
                supported_count += 1
                try:
                    rep = inspect_single_file(item)
                    if rep.suspicious:
                        suspicious_count += 1
                    reports.append(rep.to_dict())
                except Exception as ex:
                    reports.append({
                        "file_path": str(item),
                        "file_name": item.name,
                        "error": str(ex),
                        "suspicious": False,
                    })

    return BatchProcessSummary(
        directory=str(dir_path),
        total_files_scanned=total_scanned,
        supported_files_count=supported_count,
        suspicious_count=suspicious_count,
        file_reports=reports,
    )


def batch_clean(
    dir_path: Path,
    output_dir: Path | None = None,
    recursive: bool = True,
    in_place: bool = False,
) -> BatchProcessSummary:
    """Clean all supported files in a directory tree."""
    dir_path = Path(dir_path).resolve()
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path}")

    if not in_place and output_dir is None:
        raise ValueError("Must specify output_dir or enable in_place=True for batch cleaning.")

    out_root = Path(output_dir).resolve() if output_dir else dir_path
    if output_dir:
        out_root.mkdir(parents=True, exist_ok=True)

    total_scanned = 0
    supported_count = 0
    cleaned_count = 0
    failed_count = 0
    reports: list[dict[str, Any]] = []

    pattern = "**/*" if recursive else "*"
    for item in dir_path.glob(pattern):
        if item.is_file():
            total_scanned += 1
            if item.suffix.lower() in ALL_SUPPORTED_EXTS:
                supported_count += 1
                
                # Determine destination path preserving directory structure
                if in_place:
                    dest = item
                else:
                    rel = item.relative_to(dir_path)
                    dest = out_root / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)

                try:
                    res = clean_single_file(item, dest)
                    if res.success:
                        cleaned_count += 1
                    else:
                        failed_count += 1
                    reports.append(res.to_dict())
                except Exception as ex:
                    failed_count += 1
                    reports.append({
                        "input_path": str(item),
                        "output_path": str(dest),
                        "success": False,
                        "error": str(ex),
                    })

    return BatchProcessSummary(
        directory=str(dir_path),
        total_files_scanned=total_scanned,
        supported_files_count=supported_count,
        cleaned_count=cleaned_count,
        failed_count=failed_count,
        file_reports=reports,
    )
