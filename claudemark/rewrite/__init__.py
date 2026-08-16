"""Statistical watermark disruption and evaluation module for ClaudeMark."""

from .base import RewriteEvaluation, RewriteProvider, RewriteResult
from .evaluation import evaluate_rewrite
from .paraphrase import disrupt_watermark
from .transforms import rebalance_cadence, substitute_synonyms

__all__ = [
    "RewriteResult",
    "RewriteEvaluation",
    "RewriteProvider",
    "disrupt_watermark",
    "evaluate_rewrite",
    "substitute_synonyms",
    "rebalance_cadence",
]
