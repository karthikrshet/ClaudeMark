"""Base interfaces and data structures for ClaudeMark watermark analyzers."""

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
    assumptions: list[str]
    confidence_interpretation: str
    limitations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WatermarkResult:
    """Standardized result produced by watermark detectors."""
    algorithm_name: str
    algorithm_version: str
    signal_score: float  # 0.0 to 1.0
    confidence: float    # 0.0 to 1.0
    status: str          # "clean_or_low_signal" | "potential_signal" | "strong_signal"
    interpretation: str
    threshold: float
    features: dict[str, float] = field(default_factory=dict)
    hypothesis: StatisticalHypothesis | None = None
    limitations: list[str] = field(default_factory=lambda: [
        "This is a probabilistic research result.",
        "The result does not prove Claude or AI authorship.",
        "Statistical properties can naturally vary across genres, domains, and human authors.",
    ])

    @property
    def composite_score(self) -> float:
        """Alias for signal_score; the primary composite watermark signal (0.0–1.0)."""
        return self.signal_score

    @property
    def is_watermarked(self) -> bool:
        """Return True if signal_score meets or exceeds threshold."""
        return self.signal_score >= self.threshold

    def to_dict(self) -> dict[str, Any]:
        res = asdict(self)
        res["composite_score"] = self.signal_score  # explicit alias in serialized form
        res["is_watermarked"] = self.is_watermarked
        return res


class WatermarkAnalyzer(ABC):
    """Abstract base class for all watermark analysis algorithms."""

    def __init__(self, name: str, version: str, threshold: float = 0.65) -> None:
        self.name = name
        self.version = version
        self.threshold = threshold

    @abstractmethod
    def analyze(self, text: str) -> WatermarkResult:
        """Perform full statistical analysis and return structured result."""
        raise NotImplementedError

    def score(self, text: str) -> float:
        """Convenience method returning just the signal score between 0.0 and 1.0."""
        return self.analyze(text).signal_score

    def explain(self, text: str) -> str:
        """Return a human-readable scientific explanation of the analysis."""
        res = self.analyze(text)
        return f"{res.algorithm_name} (v{res.algorithm_version}): score={res.signal_score:.2f}, confidence={res.confidence * 100:.1f}%. {res.interpretation}"

    def report(self, text: str) -> dict[str, Any]:
        """Return full analysis serialized as a dictionary."""
        return self.analyze(text).to_dict()
