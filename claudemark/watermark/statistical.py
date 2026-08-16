"""Statistical testing and distribution modeling for ClaudeMark."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

_WORD_RE = re.compile(r"\b[^\W\d_]+(?:'[^\W\d_]+)?\b", re.UNICODE)


def normal_cdf(z: float) -> float:
    """Standard normal cumulative distribution function (CDF) via erf."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def z_to_p_value(z: float, two_tailed: bool = True) -> float:
    """Convert a z-score to a p-value."""
    cdf = normal_cdf(abs(z))
    p = 1.0 - cdf
    return 2.0 * p if two_tailed else p


def compute_shannon_entropy(items: list[Any]) -> float:
    """Calculate Shannon entropy in bits."""
    if not items:
        return 0.0
    counts = Counter(items)
    n = len(items)
    return -sum((c / n) * math.log2(c / n) for c in counts.values() if c > 0)


def compute_ngram_entropy(words: list[str], n: int = 2) -> float:
    """Calculate the entropy of n-gram sequences."""
    if len(words) < n:
        return 0.0
    ngrams = [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]
    return compute_shannon_entropy(ngrams)


def compute_burstiness(sentence_lengths: list[int]) -> float:
    """Compute the burstiness index of sentence lengths: (std_dev - mean) / (std_dev + mean).
    Values near -1 indicate uniform spacing (typical of some generated text); values > 0 indicate human burstiness.
    """
    if len(sentence_lengths) < 2:
        return 0.0
    mean = sum(sentence_lengths) / len(sentence_lengths)
    if mean == 0:
        return 0.0
    var = sum((x - mean) ** 2 for x in sentence_lengths) / len(sentence_lengths)
    std_dev = math.sqrt(var)
    if (std_dev + mean) == 0:
        return 0.0
    return (std_dev - mean) / (std_dev + mean)


def compute_yules_k(words: list[str]) -> float:
    """Compute Yule's characteristic K metric for vocabulary richness.
    Higher values indicate repetitive/formulaic vocabulary; lower values indicate rich/diverse vocabulary.
    """
    if not words:
        return 0.0
    n = len(words)
    counts = Counter(words)
    sum_m2 = sum(f * (f - 1) for f in counts.values())
    if n <= 1:
        return 0.0
    return 10000.0 * (sum_m2 / (n * n))


def compute_token_transition_regularity(words: list[str]) -> float:
    """Evaluate local bigram transition log-probability consistency.
    Statistical watermarking often modifies token choice probabilities, smoothing or altering transition distributions.
    """
    if len(words) < 3:
        return 0.5
    bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)]
    counts = Counter(bigrams)
    total_bigrams = len(bigrams)
    # Transition probability entropy
    ent = compute_shannon_entropy(bigrams)
    max_ent = math.log2(total_bigrams) if total_bigrams > 1 else 1.0
    normalized_entropy = (ent / max_ent) if max_ent > 0 else 1.0
    return normalized_entropy
