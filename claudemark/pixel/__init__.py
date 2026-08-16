"""Pixel-domain watermark research and forensics module for ClaudeMark."""

from .base import PixelAnalysisReport, PixelPurificationResult, PixelWatermarkBackend
from .evaluation import compare_image_hashes, compute_pixel_hashes
from .registry import pixel_registry

__all__ = [
    "PixelWatermarkBackend",
    "PixelAnalysisReport",
    "PixelPurificationResult",
    "pixel_registry",
    "compute_pixel_hashes",
    "compare_image_hashes",
]
