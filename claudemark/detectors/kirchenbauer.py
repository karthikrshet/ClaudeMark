"""Kirchenbauer-style statistical red/green token watermark research detector."""

from __future__ import annotations

import hashlib
import math
import re
from typing import Any

from ..watermark.statistical import z_to_p_value
from .base import DetectionResult, StatisticalHypothesis, WatermarkDetector

_WORD_RE = re.compile(r"\b[^\W\d_]+(?:'[^\W\d_]+)?\b", re.UNICODE)


class KirchenbauerDetector(WatermarkDetector):
    """Statistical research detector modeling Kirchenbauer et al. (2023)
    red/green list token watermarks.
    
    Evaluates whether subsequent tokens fall into pseudo-random green lists
    seeded by preceding token n-grams with higher probability than expected by chance.
    """

    def __init__(self, gamma: float = 0.5, z_threshold: float = 4.0, version: str = "0.1.0") -> None:
        super().__init__(
            name="Kirchenbauer Red/Green Statistical Detector",
            version=version,
            threshold=0.65,
        )
        self.gamma = gamma
        self.z_threshold = z_threshold

    def _is_green(self, prefix: str, token: str) -> bool:
        """Deterministic pseudo-random hash test for green list membership."""
        seed = f"{prefix}:{token}".encode("utf-8")
        h = int(hashlib.sha256(seed).hexdigest()[:8], 16)
        return (h / 0xFFFFFFFF) < self.gamma

    def detect(self, text: str) -> DetectionResult:
        words = _WORD_RE.findall(text.lower())
        n = len(words)
        
        if n < 10:
            return DetectionResult(
                algorithm_name=self.name,
                algorithm_version=self.version,
                signal_score=0.0,
                confidence=0.1,
                status="clean_or_low_signal",
                interpretation="Text sample is too short for Kirchenbauer z-score testing (minimum 10 tokens required).",
                threshold=self.threshold,
                features={"token_count": n},
            )

        # Count green tokens given previous token prefix
        green_count = 0
        total_tested = n - 1
        for i in range(1, n):
            prefix = words[i - 1]
            curr = words[i]
            if self._is_green(prefix, curr):
                green_count += 1

        expected = self.gamma * total_tested
        variance = total_tested * self.gamma * (1.0 - self.gamma)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0
        
        z_score = (green_count - expected) / std_dev
        p_val = z_to_p_value(z_score, two_tailed=False) if z_score > 0 else 1.0
        
        # Normalize score between 0 and 1 (z=4.0 corresponds to ~0.80)
        norm_score = 1.0 / (1.0 + math.exp(-0.7 * (z_score - 2.0)))
        signal_score = round(max(0.0, min(1.0, norm_score)), 4)
        confidence = round(min(0.99, max(0.20, 0.4 + 0.6 * (total_tested / 200.0))), 4)
        
        status = "potential_signal" if signal_score >= self.threshold else "clean_or_low_signal"
        if z_score >= self.z_threshold:
            status = "strong_signal"

        interpretation = (
            f"Kirchenbauer test found {green_count}/{total_tested} green tokens (z = {z_score:.2f}, p = {p_val:.5e}). "
            f"Status: {status.upper().replace('_', ' ')}."
        )

        features = {
            "token_count": n,
            "green_tokens": green_count,
            "expected_green": round(expected, 2),
            "green_ratio": round(green_count / total_tested, 4) if total_tested > 0 else 0.0,
            "z_score": round(z_score, 4),
            "gamma": self.gamma,
        }

        hypothesis = StatisticalHypothesis(
            null_hypothesis="H0: Tokens are selected without green-list bias (binomial parameter p = gamma).",
            alternative_hypothesis="H1: Tokens are systematically biased toward the green list (p > gamma).",
            test_statistic_name="Kirchenbauer Z-Score",
            test_statistic_value=round(z_score, 4),
            p_value=round(p_val, 6),
            assumptions=[
                "Independent token transition sampling",
                "Approximation by normal distribution valid for N > 30",
            ],
            confidence_interpretation=f"p = {p_val:.5e} indicates the probability of this green-token density under unwatermarked generation.",
            limitations=[
                "Detector uses standard generic pseudo-random seeding; custom model secret keys cannot be verified without their exact seed matrix.",
            ],
        )

        return DetectionResult(
            algorithm_name=self.name,
            algorithm_version=self.version,
            signal_score=signal_score,
            confidence=confidence,
            status=status,
            interpretation=interpretation,
            threshold=self.threshold,
            features=features,
            hypothesis=hypothesis,
        )
