"""Registry for pluggable pixel-domain watermark backends."""

from __future__ import annotations

from typing import Any

from .adapters import (
    CtrlRegenBackend,
    MarkDiffusionBackend,
    StableSignatureBackend,
    StegaStampBackend,
    SynthIDImageBackend,
    TreeRingBackend,
)
from .base import PixelWatermarkBackend


class PixelBackendRegistry:
    """Registry for pixel-domain watermark research backends."""

    def __init__(self) -> None:
        self._backends: dict[str, PixelWatermarkBackend] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(SynthIDImageBackend())
        self.register(CtrlRegenBackend())
        self.register(MarkDiffusionBackend())
        self.register(TreeRingBackend())
        self.register(StableSignatureBackend())
        self.register(StegaStampBackend())

    def register(self, backend: PixelWatermarkBackend) -> None:
        self._backends[backend.name.lower()] = backend

    def get(self, name: str) -> PixelWatermarkBackend:
        backend = self._backends.get(name.lower())
        if not backend:
            raise KeyError(f"Pixel backend '{name}' not found. Available: {self.list_backends()}")
        return backend

    def list_backends(self) -> list[str]:
        return sorted(self._backends.keys())

    def list_details(self) -> list[dict[str, Any]]:
        return [
            {
                "name": b.name,
                "version": b.version,
                "available": b.is_available(),
            }
            for b in self._backends.values()
        ]


pixel_registry = PixelBackendRegistry()
