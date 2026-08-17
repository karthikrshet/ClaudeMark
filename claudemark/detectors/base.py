"""Base classes and standardized interfaces for ClaudeMark watermark detectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class StatisticalHypothesis:
    """Rigorous documentation of the statistical hypothesis test used."""
    null_hypothesis: str
    alternative_hypothesis: str
    test_statistic_name: str
    test_statistic_value: float
    p_value: float | None
    assumptions: list[str] = field(default_factory=list)
    confidence_interpretation: str = ""
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DetectionResult:
    """Standardized detection result across all pluggable detectors."""
    algorithm_name: str
    algorithm_version: str
    signal_score: float  # 0.0 to 1.0
    confidence: float    # 0.0 to 1.0
    status: str          # "clean_or_low_signal" | "potential_signal" | "strong_signal"
    interpretation: str
    threshold: float
    features: dict[str, Any] = field(default_factory=dict)
    hypothesis: StatisticalHypothesis | None = None
    limitations: list[str] = field(default_factory=lambda: [
        "This is a probabilistic research result.",
        "The result does not constitute proof of model origin or human/AI authorship.",
        "Statistical properties can vary across genres, domains, and human authors.",
    ])

    @property
    def is_watermarked(self) -> bool:
        return self.signal_score >= self.threshold

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["is_watermarked"] = self.is_watermarked
        return d


class WatermarkDetector(ABC):
    """Abstract base class for all pluggable watermark detection algorithms.
    
    Standardized Detector Contract:
        detector.detect(text)      -> DetectionResult
        detector.analyze(text)     -> DetectionResult (alias)
        detector.score(text)       -> float (0.0 to 1.0)
        detector.explain(text)     -> str (human-readable interpretation)
        detector.limitations()     -> list[str]
    """

    def __init__(self, name: str, version: str = "0.1.0", threshold: float = 0.65) -> None:
        self.name = name
        self.version = version
        self.threshold = threshold

    @abstractmethod
    def detect(self, text: str) -> DetectionResult:
        """Execute detection and return structured result."""
        raise NotImplementedError

    def analyze(self, text: str) -> DetectionResult:
        """Alias for detect() providing consistent API naming across modules."""
        return self.detect(text)

    def score(self, text: str) -> float:
        """Convenience method returning just the numeric score (0.0 to 1.0)."""
        return self.detect(text).signal_score

    def explain(self, text: str) -> str:
        """Return a human-readable explanation of the analysis."""
        res = self.detect(text)
        return (
            f"[{res.algorithm_name} v{res.algorithm_version}] "
            f"Score: {res.signal_score:.2f} (Confidence: {res.confidence * 100:.0f}%, Status: {res.status.upper()}). "
            f"{res.interpretation}"
        )

    def limitations(self) -> list[str]:
        """Return the documented limitations and scientific constraints of this detector."""
        return [
            "This detector is a probabilistic research instrument.",
            "Results do not prove model origin or human/AI authorship.",
            "Text length, genre, and technical register can alter distribution metrics.",
        ]
