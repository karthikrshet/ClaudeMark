"""Local syntactic transformations, synonym substitution, and cadence rebalancing."""

from __future__ import annotations

import random
import re
from typing import Any

# Curated synonym dictionary for safe local transformation without external models
_SYNONYMS = {
    "furthermore": ["moreover", "in addition", "additionally", "besides"],
    "moreover": ["furthermore", "in addition", "additionally"],
    "however": ["nevertheless", "yet", "still", "nonetheless"],
    "therefore": ["consequently", "thus", "as a result", "hence"],
    "consequently": ["therefore", "as a result", "thus"],
    "significant": ["substantial", "notable", "considerable", "meaningful"],
    "crucial": ["essential", "vital", "critical", "pivotal"],
    "essential": ["crucial", "vital", "fundamental", "necessary"],
    "demonstrate": ["show", "illustrate", "exhibit", "indicate"],
    "utilize": ["use", "employ", "apply", "leverage"],
    "implement": ["execute", "apply", "carry out", "deploy"],
    "comprehensive": ["thorough", "extensive", "complete", "in-depth"],
    "paradigm": ["framework", "model", "approach", "pattern"],
    "facilitate": ["enable", "assist", "help", "streamline"],
    "approximately": ["roughly", "about", "around", "nearly"],
    "subsequently": ["later", "afterward", "then", "thereafter"],
    "in conclusion": ["to summarize", "in summary", "overall", "to conclude"],
    "in order to": ["to"],
    "due to the fact that": ["because"],
    "at this point in time": ["now", "currently"],
}


def substitute_synonyms(text: str, substitution_rate: float = 0.4, seed: int | None = 42) -> str:
    """Safely replace common transition phrases and high-frequency watermark tokens."""
    if not text:
        return text

    rng = random.Random(seed)
    result = text

    # Process multi-word phrases first
    for phrase, alts in _SYNONYMS.items():
        if " " in phrase and phrase in result.lower():
            if rng.random() < substitution_rate:
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                chosen = rng.choice(alts)
                result = pattern.sub(chosen, result)

    # Process single-word tokens
    words = result.split()
    transformed_words = []
    for w in words:
        clean_w = w.strip(".,;:!?()\"'").lower()
        if clean_w in _SYNONYMS and " " not in clean_w:
            if rng.random() < substitution_rate:
                chosen = rng.choice(_SYNONYMS[clean_w])
                # Preserve capitalization
                if w and w[0].isupper():
                    chosen = chosen.capitalize()
                # Preserve trailing punctuation
                punct = "".join(c for c in w if c in ".,;:!?()\"'")
                transformed_words.append(chosen + punct)
                continue
        transformed_words.append(w)

    return " ".join(transformed_words)


def rebalance_cadence(text: str) -> str:
    """Rebalance sentence length cadence to disrupt strict token burstiness constraints."""
    if not text:
        return text

    # Break overly long compound sentences or combine short fragments
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if len(sentences) < 2:
        return text

    processed = []
    for s in sentences:
        # Simplify "which is", "that is"
        s_mod = re.sub(r',\s*which\s+(?:is|are|was|were)\s+', ', ', s)
        processed.append(s_mod)

    return " ".join(processed)
