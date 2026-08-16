"""Base classes for pixel-domain watermark research and purification adapters.

Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PixelAnalysisReport:
    """Standardized report for pixel-domain watermark analysis."""
    backend_name: str
    backend_version: str
    available: bool
    score: float = 0.0
    detected: bool = False
    confidence: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=lambda: [
        "Pixel-domain watermark detection is probabilistic.",
        "Requires specific model checkpoints for target architectures.",
        "Local execution only; external dependencies must be installed explicitly.",
    ])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PixelPurificationResult:
    """Result of an experimental pixel-domain watermark disruption/purification."""
    backend_name: str
    input_path: str
    output_path: str | None
    success: bool
    actions_performed: list[str] = field(default_factory=list)
    perceptual_similarity: float = 1.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PixelWatermarkBackend(ABC):
    """Abstract interface for pixel-domain watermark research backends."""

    def __init__(self, name: str, version: str = "0.1.0") -> None:
        self.name = name
        self.version = version

    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend dependencies (e.g. PyTorch, diffusion models) are installed."""
        raise NotImplementedError

    @abstractmethod
    def inspect(self, image_path: Path) -> PixelAnalysisReport:
        """Inspect image for pixel-domain watermarks."""
        raise NotImplementedError

    @abstractmethod
    def purify(self, image_path: Path, output_path: Path | None = None) -> PixelPurificationResult:
        """Execute experimental pixel-domain purification if backend is available."""
        raise NotImplementedError
