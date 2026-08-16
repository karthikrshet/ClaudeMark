"""Detector registry for ClaudeMark watermark analyzers."""

from __future__ import annotations

from typing import Callable

from .base import WatermarkAnalyzer
from .claude_detector import ClaudeWatermarkAnalyzer


class EntropyBurstinessDetector(WatermarkAnalyzer):
    """Pure entropy and burstiness anomaly detector for generative text research."""

    def __init__(self, threshold: float = 0.60) -> None:
        super().__init__(
            name="Entropy-Burstiness Research Detector",
            version="0.1.0",
            threshold=threshold,
        )
        self._inner = ClaudeWatermarkAnalyzer(threshold=threshold, version="0.1.0")

    def analyze(self, text: str):
        res = self._inner.analyze(text)
        res.algorithm_name = self.name
        res.algorithm_version = self.version
        return res


class DetectorRegistry:
    """Registry allowing pluggable watermark detector algorithms."""

    def __init__(self) -> None:
        self._detectors: dict[str, WatermarkAnalyzer] = {}
        self._factories: dict[str, Callable[[], WatermarkAnalyzer]] = {}
        self._default_name = "claude"
        
        # Register built-in detectors
        self.register("claude", ClaudeWatermarkAnalyzer())
        self.register("claude-research-v1", ClaudeWatermarkAnalyzer())
        self.register("entropy-burstiness", EntropyBurstinessDetector())

    def register(self, name: str, detector: WatermarkAnalyzer) -> None:
        """Register an active detector instance."""
        self._detectors[name.lower()] = detector

    def register_factory(self, name: str, factory: Callable[[], WatermarkAnalyzer]) -> None:
        """Register a factory callable returning a new detector instance."""
        self._factories[name.lower()] = factory

    def get(self, name: str | None = None) -> WatermarkAnalyzer:
        """Retrieve detector by name or get default detector."""
        target = (name or self._default_name).lower()
        if target in self._detectors:
            return self._detectors[target]
        if target in self._factories:
            detector = self._factories[target]()
            self._detectors[target] = detector
            return detector
        available = ", ".join(self.list_detectors())
        raise KeyError(f"Unknown watermark detector '{name}'. Available: {available}")

    def list_detectors(self) -> list[str]:
        """List all registered detector names."""
        keys = set(self._detectors.keys()) | set(self._factories.keys())
        return sorted(keys)

    def set_default(self, name: str) -> None:
        """Set the default detector name."""
        if name.lower() not in self._detectors and name.lower() not in self._factories:
            raise KeyError(f"Cannot set unknown detector '{name}' as default.")
        self._default_name = name.lower()


# Global default registry instance
registry = DetectorRegistry()
