"""SynthID-style research adapter and token distribution scorer."""

from __future__ import annotations

import math
import re
from typing import Any

from ..watermark.statistical import compute_shannon_entropy, compute_yules_k, z_to_p_value
from .base import DetectionResult, StatisticalHypothesis, WatermarkDetector

_WORD_RE = re.compile(r"\b[^\W\d_]+(?:'[^\W\d_]+)?\b", re.UNICODE)


class SynthIDDetector(WatermarkDetector):
    """SynthID-style research analyzer modeling token probability modulation
    and entropy deformation in generative language models.
    """

    def __init__(self, threshold: float = 0.65, version: str = "0.1.0") -> None:
        super().__init__(
            name="SynthID-Style Research Detector",
            version=version,
            threshold=threshold,
        )

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
                interpretation="Insufficient text length for SynthID distribution analysis.",
                threshold=self.threshold,
                features={"word_count": n},
            )

        # Evaluate token entropy smoothing and frequency compression
        entropy = compute_shannon_entropy(words)
        max_ent = math.log2(n) if n > 1 else 1.0
        ratio = entropy / max_ent if max_ent > 0 else 1.0
        yule = compute_yules_k(words)
        
        # SynthID score heuristic
        z = ((0.80 - ratio) / 0.10) + ((yule - 80.0) / 30.0)
        score = 1.0 / (1.0 + math.exp(-0.6 * z))
        signal_score = round(max(0.0, min(1.0, score)), 4)
        
        status = "potential_signal" if signal_score >= self.threshold else "clean_or_low_signal"
        p_val = z_to_p_value(z, two_tailed=False)

        return DetectionResult(
            algorithm_name=self.name,
            algorithm_version=self.version,
            signal_score=signal_score,
            confidence=round(min(0.95, 0.4 + 0.5 * (n / 300.0)), 4),
            status=status,
            interpretation=(
                f"SynthID-style research model evaluated token modulation (score: {signal_score:.2f}, p = {p_val:.4f}). "
                f"Status: {status.upper().replace('_', ' ')}."
            ),
            threshold=self.threshold,
            features={"entropy": round(entropy, 4), "entropy_ratio": round(ratio, 4), "yule_k": round(yule, 2)},
            hypothesis=StatisticalHypothesis(
                null_hypothesis="H0: Token entropy distribution matches unwatermarked natural language.",
                alternative_hypothesis="H1: Token entropy distribution exhibits SynthID-style perturbation.",
                test_statistic_name="Entropy Modulation Z",
                test_statistic_value=round(z, 4),
                p_value=round(p_val, 5),
                assumptions=["Independent vocabulary frequencies"],
                confidence_interpretation="Research approximation based on publicly documented SynthID principles.",
                limitations=["Google's production SynthID keying is proprietary and cannot be verified locally."],
            ),
        )
