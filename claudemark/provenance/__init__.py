"""ClaudeMark file provenance inspection, metadata stripping, and batch processing subpackage."""

from .base import (
    BatchProcessSummary,
    FileCleaningReport,
    ProvenanceInspectionReport,
)
from .batch import (
    ALL_SUPPORTED_EXTS,
    batch_clean,
    batch_inspect,
    clean_single_file,
    inspect_single_file,
)
from .c2pa import inspect_c2pa_bytes, inspect_c2pa_tool
from .documents import clean_document, inspect_document
from .exif_xmp import inspect_exif_xmp_bytes
from .images import clean_image_file, inspect_image_file

__all__ = [
    "ProvenanceInspectionReport",
    "FileCleaningReport",
    "BatchProcessSummary",
    "inspect_single_file",
    "clean_single_file",
    "batch_inspect",
    "batch_clean",
    "inspect_c2pa_bytes",
    "inspect_c2pa_tool",
    "inspect_exif_xmp_bytes",
    "inspect_document",
    "clean_document",
    "inspect_image_file",
    "clean_image_file",
    "ALL_SUPPORTED_EXTS",
]
