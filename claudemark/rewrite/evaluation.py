"""Comprehensive before/after evaluation for watermark score shift, similarity, and edit distance."""

from __future__ import annotations

import difflib
from typing import Any

from ..core.text_stats import calculate_entropy
from ..detectors.registry import detector_registry
from .base import RewriteEvaluation


def evaluate_rewrite(
    original_text: str,
    rewritten_text: str,
    detector_name: str = "claude",
) -> RewriteEvaluation:
    """Compute comprehensive forensic comparison between original and transformed texts."""
    detector = detector_registry.get(detector_name)
    orig_score = detector.score(original_text)
    rewritten_score = detector.score(rewritten_text)
    score_delta = rewritten_score - orig_score

    # Character and word differences
    orig_len = len(original_text)
    rewritten_len = len(rewritten_text)
    matcher = difflib.SequenceMatcher(None, original_text, rewritten_text)
    similarity = matcher.ratio()  # 0.0 to 1.0

    orig_words = original_text.lower().split()
    rewritten_words = rewritten_text.lower().split()
    word_matcher = difflib.SequenceMatcher(None, orig_words, rewritten_words)
    word_sim = word_matcher.ratio()

    char_change_pct = (abs(rewritten_len - orig_len) / orig_len * 100.0) if orig_len > 0 else 0.0
    word_change_pct = (1.0 - word_sim) * 100.0

    # Entropy shifts
    orig_entropy = calculate_entropy(list(original_text))
    rewritten_entropy = calculate_entropy(list(rewritten_text))
    entropy_delta = rewritten_entropy - orig_entropy

    return RewriteEvaluation(
        original_watermark_score=orig_score,
        rewritten_watermark_score=rewritten_score,
        watermark_score_delta=score_delta,
        semantic_similarity=round(similarity, 4),
        character_change_ratio=round(char_change_pct, 2),
        word_change_ratio=round(word_change_pct, 2),
        levenshtein_similarity=round(similarity, 4),
        original_entropy=round(orig_entropy, 3),
        rewritten_entropy=round(rewritten_entropy, 3),
        entropy_delta=round(entropy_delta, 3),
    )
