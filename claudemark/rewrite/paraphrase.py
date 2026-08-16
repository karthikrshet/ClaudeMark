"""High-level paraphrasing and statistical watermark disruption coordinator."""

from __future__ import annotations

from typing import Any

from .base import RewriteEvaluation, RewriteResult
from .evaluation import evaluate_rewrite
from .transforms import rebalance_cadence, substitute_synonyms


def disrupt_watermark(
    text: str,
    strategy: str = "synonym_cadence",
    detector_name: str = "claude",
    substitution_rate: float = 0.4,
    seed: int | None = 42,
) -> RewriteResult:
    """Execute best-effort local statistical watermark disruption on text."""
    if not text or not text.strip():
        return RewriteResult(
            original_text=text,
            rewritten_text=text,
            strategy_name=strategy,
            provider_name="local_rule_based",
            success=True,
        )

    # Step 1: Synonym rotation & transition rebalancing
    transformed = substitute_synonyms(text, substitution_rate=substitution_rate, seed=seed)
    
    # Step 2: Cadence restructuring
    if strategy in ("synonym_cadence", "cadence_only"):
        transformed = rebalance_cadence(transformed)

    # Step 3: Evaluate before and after
    eval_result = evaluate_rewrite(text, transformed, detector_name=detector_name)

    return RewriteResult(
        original_text=text,
        rewritten_text=transformed,
        strategy_name=strategy,
        provider_name="local_rule_based",
        evaluation=eval_result,
        success=True,
    )
