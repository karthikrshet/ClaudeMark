"""Claude-focused statistical AI text watermark research analyzer."""

from __future__ import annotations

import math
import re
from typing import Any

from .base import StatisticalHypothesis, WatermarkAnalyzer, WatermarkResult
from .statistical import (
    compute_burstiness,
    compute_ngram_entropy,
    compute_shannon_entropy,
    compute_token_transition_regularity,
    compute_yules_k,
    z_to_p_value,
)

_WORD_RE = re.compile(r"\b[^\W\d_]+(?:'[^\W\d_]+)?\b", re.UNICODE)
_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'])')

# Typical human baseline calibration constants for natural English prose
HUMAN_BASELINE = {
    "avg_burstiness": 0.18,
    "burstiness_std": 0.15,
    "avg_entropy_ratio": 0.85,
    "entropy_std": 0.08,
    "avg_yule_k": 85.0,
    "yule_std": 25.0,
}


class ClaudeWatermarkAnalyzer(WatermarkAnalyzer):
    """Statistical research detector modeling structural predictability,
    vocabulary compression, token transition distributions, and sentence burstiness.
    
    This detector provides forensic indicators for academic research into AI text
    generation characteristics and statistical sampling watermarks.
    """

    def __init__(self, threshold: float = 0.65, version: str = "0.1.0") -> None:
        super().__init__(
            name="ClaudeMark Claude Research Detector",
            version=version,
            threshold=threshold,
        )

    def analyze(self, text: str) -> WatermarkResult:
        if not text or len(text.strip()) < 20:
            return WatermarkResult(
                algorithm_name=self.name,
                algorithm_version=self.version,
                signal_score=0.0,
                confidence=0.1,
                status="clean_or_low_signal",
                interpretation="Text sample is too short for reliable statistical evaluation (minimum 20 characters required).",
                threshold=self.threshold,
                features={"word_count": 0},
            )

        words = _WORD_RE.findall(text.lower())
        word_count = len(words)
        
        if word_count < 5:
            return WatermarkResult(
                algorithm_name=self.name,
                algorithm_version=self.version,
                signal_score=0.0,
                confidence=0.2,
                status="clean_or_low_signal",
                interpretation="Insufficient word count for statistical analysis (minimum 5 words required).",
                threshold=self.threshold,
                features={"word_count": word_count},
            )

        # 1. Sentences & Burstiness
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        sentences: list[str] = []
        for p in paragraphs:
            splits = _SENTENCE_SPLIT_RE.split(p)
            for s in splits:
                if s.strip():
                    sentences.append(s.strip())
        
        sent_lengths = [len(_WORD_RE.findall(s)) for s in sentences if s]
        if not sent_lengths:
            sent_lengths = [word_count]
            
        burstiness = compute_burstiness(sent_lengths)
        
        # 2. Entropy & Transition regularity
        unigram_entropy = compute_shannon_entropy(words)
        max_possible_entropy = math.log2(word_count) if word_count > 1 else 1.0
        entropy_ratio = (unigram_entropy / max_possible_entropy) if max_possible_entropy > 0 else 1.0
        
        bigram_entropy = compute_ngram_entropy(words, n=2)
        transition_reg = compute_token_transition_regularity(words)
        
        # 3. Vocabulary Richness (Yule's K)
        yule_k = compute_yules_k(words)
        
        # 4. Statistical hypothesis testing & score calculation
        # Normalized z-deviations from typical human baseline
        z_burst = (HUMAN_BASELINE["avg_burstiness"] - burstiness) / HUMAN_BASELINE["burstiness_std"]
        z_entropy = (HUMAN_BASELINE["avg_entropy_ratio"] - entropy_ratio) / HUMAN_BASELINE["entropy_std"]
        z_yule = (yule_k - HUMAN_BASELINE["avg_yule_k"]) / HUMAN_BASELINE["yule_std"]
        
        # Aggregate composite z-score
        composite_z = (0.45 * z_burst) + (0.35 * z_entropy) + (0.20 * z_yule)
        p_val = z_to_p_value(composite_z, two_tailed=False)
        
        # Convert to 0.0 - 1.0 sigmoid probability score
        raw_score = 1.0 / (1.0 + math.exp(-0.8 * composite_z))
        
        # Sample size confidence scaling (higher confidence with longer text)
        size_factor = min(1.0, math.log10(max(10, word_count)) / 3.0)  # reaches 1.0 around 1,000 words
        confidence = round(min(0.99, max(0.20, 0.4 + 0.6 * size_factor * (abs(raw_score - 0.5) * 2))), 4)
        
        signal_score = round(raw_score, 4)
        
        # Determine status
        if signal_score >= self.threshold:
            status = "strong_signal" if signal_score >= 0.80 else "potential_signal"
            interpretation = (
                f"The text exhibits statistical characteristics consistent with the configured research detector "
                f"(signal score: {signal_score:.2f}, confidence: {confidence * 100:.0f}%). "
                f"This indicates elevated structural regularity or low burstiness, but does NOT prove Claude or AI authorship."
            )
        else:
            status = "clean_or_low_signal"
            interpretation = (
                f"No significant statistical watermark signals detected (signal score: {signal_score:.2f}, "
                f"confidence: {confidence * 100:.0f}%). Text distribution falls within typical baseline variance."
            )

        features = {
            "word_count": float(word_count),
            "sentence_count": float(len(sentences)),
            "burstiness_index": round(burstiness, 4),
            "unigram_entropy": round(unigram_entropy, 4),
            "entropy_ratio": round(entropy_ratio, 4),
            "bigram_entropy": round(bigram_entropy, 4),
            "transition_regularity": round(transition_reg, 4),
            "yules_characteristic_k": round(yule_k, 2),
            "composite_z_score": round(composite_z, 4),
        }

        hypothesis = StatisticalHypothesis(
            null_hypothesis="H0: The text is generated from an unconstrained human or natural language distribution.",
            alternative_hypothesis="H1: The text exhibits statistical uniformity and entropy constraints consistent with model sampling.",
            test_statistic_name="Composite Deviation Z-Score",
            test_statistic_value=round(composite_z, 4),
            p_value=round(p_val, 5),
            assumptions=[
                "Independent token distribution approximations",
                "Baseline calibrated on standard English natural prose",
                "Sample size sufficient for asymptotic normality",
            ],
            confidence_interpretation=f"p = {p_val:.5f} represents the probability of observing these structural characteristics under H0.",
            limitations=[
                "Formal, academic, or legal texts naturally exhibit lower burstiness without being AI-generated.",
                "Short texts (<100 words) have high variance and lower diagnostic power.",
                "This detector is a statistical research instrument and must not be used as definitive proof.",
            ],
        )

        return WatermarkResult(
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
