"""Generic entropy and burstiness statistical watermark detector."""

from __future__ import annotations

import math
import re
from typing import Any

from ..watermark.statistical import compute_burstiness, compute_shannon_entropy
from .base import DetectionResult, StatisticalHypothesis, WatermarkDetector

_WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:'[A-Za-z0-9_]+)?")
_SENTENCE_SPLIT_RE = re.compile(r"[.!?]+\s+")


class GenericEntropyDetector(WatermarkDetector):
    """Generic baseline detector measuring lexical entropy and sentence burstiness."""

    def __init__(self, threshold: float = 0.60, version: str = "0.1.0") -> None:
        super().__init__(
            name="Generic Entropy & Burstiness Detector",
            version=version,
            threshold=threshold,
        )

    def detect(self, text: str) -> DetectionResult:
        words = _WORD_RE.findall(text.lower())
        n = len(words)
        if n < 5:
            return DetectionResult(
                algorithm_name=self.name,
                algorithm_version=self.version,
                signal_score=0.0,
                confidence=0.1,
                status="clean_or_low_signal",
                interpretation="Text is too short for entropy analysis.",
                threshold=self.threshold,
            )

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        sentences: list[str] = []
        for p in paragraphs:
            for s in _SENTENCE_SPLIT_RE.split(p):
                if s.strip():
                    sentences.append(s.strip())
        
        sent_lengths = [len(_WORD_RE.findall(s)) for s in sentences if s]
        burstiness = compute_burstiness(sent_lengths) if sent_lengths else 0.0
        entropy = compute_shannon_entropy(words)
        
        # Low burstiness + low entropy indicates regularized model text
        raw_score = 0.5 * (1.0 - max(-1.0, min(1.0, burstiness)))
        signal_score = round(max(0.0, min(1.0, raw_score)), 4)
        status = "potential_signal" if signal_score >= self.threshold else "clean_or_low_signal"

        return DetectionResult(
            algorithm_name=self.name,
            algorithm_version=self.version,
            signal_score=signal_score,
            confidence=round(min(0.90, 0.3 + 0.6 * (n / 200.0)), 4),
            status=status,
            interpretation=f"Generic entropy-burstiness evaluation score: {signal_score:.2f}.",
            threshold=self.threshold,
            features={"entropy": round(entropy, 4), "burstiness": round(burstiness, 4)},
        )
