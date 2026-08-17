"""Pixel-domain watermark research backends and pluggable adapter exports.

Enables programmatic import of all pixel domain analysis and purification adapters:
- SynthID-Image
- CtrlRegen
- MarkDiffusion
- Tree-Ring
- Stable Signature
- StegaStamp

Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import (
    CtrlRegenBackend,
    MarkDiffusionBackend,
    StableSignatureBackend,
    StegaStampBackend,
    SynthIDImageBackend,
    TreeRingBackend,
)
from .base import (
    PixelAnalysisReport,
    PixelPurificationResult,
    PixelWatermarkBackend,
)
from .evaluation import compare_image_hashes, compute_pixel_hashes
from .registry import PixelBackendRegistry, pixel_registry

__all__ = [
    "PixelWatermarkBackend",
    "PixelAnalysisReport",
    "PixelPurificationResult",
    "SynthIDImageBackend",
    "CtrlRegenBackend",
    "MarkDiffusionBackend",
    "TreeRingBackend",
    "StableSignatureBackend",
    "StegaStampBackend",
    "PixelBackendRegistry",
    "pixel_registry",
    "compute_pixel_hashes",
    "compare_image_hashes",
    "get_backend",
    "list_backends",
]


def get_backend(name: str) -> PixelWatermarkBackend:
    """Retrieve registered pixel watermark backend by name."""
    return pixel_registry.get(name)


def list_backends() -> list[str]:
    """List all registered pixel watermark backend identifiers."""
    return pixel_registry.list_backends()
