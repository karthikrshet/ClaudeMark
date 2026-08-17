"""Base classes and contracts for statistical watermark disruption and rewriting in ClaudeMark.

Best-effort research toolkit for evaluating statistical watermark resilience through text transformations.
Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RewriteEvaluation:
    """Evaluation metrics comparing original and rewritten texts."""
    original_watermark_score: float
    rewritten_watermark_score: float
    watermark_score_delta: float
    semantic_similarity: float      # 0.0 to 1.0 (estimated via character/word overlap and Jaccard/edit distance)
    character_change_ratio: float   # Percentage change (0.0 to 100.0)
    word_change_ratio: float
    levenshtein_similarity: float
    original_entropy: float
    rewritten_entropy: float
    entropy_delta: float
    words_changed: int = 0
    characters_changed: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RewriteResult:
    """Standardized result of a statistical watermark disruption operation."""
    original_text: str
    rewritten_text: str
    strategy_name: str
    provider_name: str
    evaluation: RewriteEvaluation | None = None
    success: bool = True
    notes: list[str] = field(default_factory=lambda: [
        "Best-effort statistical watermark disruption.",
        "No guarantee of complete watermark removal.",
        "Semantic similarity is estimated locally.",
    ])

    @property
    def disrupted_text(self) -> str:
        """Alias for rewritten_text."""
        return self.rewritten_text

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["disrupted_text"] = self.rewritten_text
        if self.evaluation:
            d["words_changed"] = self.evaluation.words_changed
        return d


class RewriteProvider(ABC):
    """Abstract base class for rewrite and disruption engines."""

    def __init__(self, name: str, version: str = "0.1.0") -> None:
        self.name = name
        self.version = version

    @abstractmethod
    def rewrite(self, text: str, **kwargs: Any) -> str:
        """Execute text transformation or rewriting."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider dependencies or local models are ready."""
        raise NotImplementedError
