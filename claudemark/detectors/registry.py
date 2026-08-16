"""Plugin registry for pluggable ClaudeMark watermark detectors."""

from __future__ import annotations

from typing import Callable

from .base import DetectionResult, WatermarkDetector
from .claude import ClaudeWatermarkDetector
from .generic import GenericEntropyDetector
from .kirchenbauer import KirchenbauerDetector
from .synthid import SynthIDDetector


class DetectorRegistry:
    """Central registry for pluggable AI watermark detector algorithms."""

    def __init__(self) -> None:
        self._detectors: dict[str, WatermarkDetector] = {}
        self._factories: dict[str, Callable[[], WatermarkDetector]] = {}
        self._default_name = "claude"
        
        # Register core built-in detectors
        self.register("claude", ClaudeWatermarkDetector())
        self.register("claude-research-v1", ClaudeWatermarkDetector())
        self.register("kirchenbauer", KirchenbauerDetector())
        self.register("synthid", SynthIDDetector())
        self.register("generic", GenericEntropyDetector())
        self.register("entropy-burstiness", GenericEntropyDetector())

    def register(self, name: str, detector: WatermarkDetector) -> None:
        """Register an active detector instance."""
        self._detectors[name.lower()] = detector

    def register_factory(self, name: str, factory: Callable[[], WatermarkDetector]) -> None:
        """Register a lazy detector factory."""
        self._factories[name.lower()] = factory

    def get(self, name: str | None = None) -> WatermarkDetector:
        """Retrieve a detector by name or get the default."""
        target = (name or self._default_name).lower()
        if target in self._detectors:
            return self._detectors[target]
        if target in self._factories:
            det = self._factories[target]()
            self._detectors[target] = det
            return det
        available = ", ".join(self.list_detectors())
        raise KeyError(f"Unknown watermark detector '{name}'. Available: {available}")

    def list_detectors(self) -> list[str]:
        """List all available detector keys."""
        return sorted(set(self._detectors.keys()) | set(self._factories.keys()))


# Global detector registry
detector_registry = DetectorRegistry()
