"""Experimental calibration and parameter sweep tools for ClaudeMark research.

Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .base import WatermarkAnalyzer
from .claude_detector import ClaudeWatermarkAnalyzer

DEFAULT_HUMAN_SAMPLES = [
    (
        "I walked down to the harbor yesterday afternoon to watch the fishing boats come in. "
        "The salt air was crisp, and a cold gust blew from the northwest. A few gulls were "
        "circling around the wooden pilings, crying out as the fishermen sorted their catch. "
        "I stopped by the corner bakery on my way home for a loaf of sourdough and a cup of tea."
    ),
    (
        "The quick brown fox jumped over the sleeping dog in the garden. Mom was baking bread "
        "in the kitchen, and the smell of cinnamon filled the hallway. My little brother ran "
        "outside to catch butterflies while dad finished repairing the wooden fence by the shed."
    ),
    (
        "In 1928, Alexander Fleming observed that a green mold called Penicillium notatum had "
        "contaminated a Petri dish of Staphylococcus bacteria. The bacteria immediately surrounding "
        "the mold colonies had dissolved. This serendipitous discovery revolutionized modern medicine."
    ),
]

DEFAULT_SYNTHETIC_SAMPLES = [
    (
        "Furthermore, it is imperative to recognize that multifaceted methodologies facilitate "
        "holistic alignment across contemporary operational dynamics. Consequently, comprehensive "
        "strategic paradigms serve as indispensable conduits for orchestrating scalable and "
        "sustainable infrastructure modernizations across interdisciplinary organizations."
    ),
    (
        "In conclusion, the seamless integration of distributed cognitive frameworks significantly "
        "optimizes architectural resilience. Therefore, leveraging robust algorithmic methodologies "
        "ensures consistent adherence to regulatory benchmarks while enhancing systemic throughput."
    ),
    (
        "Moreover, systematic evaluations demonstrate that iterative parameter optimization "
        "yields substantial efficiencies. As a result, adopting standardized analytical protocols "
        "facilitates seamless knowledge transfer and maximizes overarching operational effectiveness."
    ),
]


@dataclass
class CalibrationEvaluation:
    threshold: float
    total_human_samples: int
    total_synthetic_samples: int
    false_positive_rate: float
    true_positive_rate: float
    accuracy: float
    f1_score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ParameterSweepResult:
    detector_name: str
    thresholds_evaluated: list[float]
    evaluations: list[CalibrationEvaluation]
    recommended_threshold: float
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_dataset(
    detector: WatermarkAnalyzer,
    human_samples: list[str],
    synthetic_samples: list[str],
    threshold: float = 0.35,
) -> CalibrationEvaluation:
    """Evaluate detector performance across human and synthetic text corpora."""
    if not human_samples:
        raise ValueError("Calibration requires non-empty human_samples (negative baseline).")
    if not synthetic_samples:
        raise ValueError("Calibration requires non-empty synthetic_samples (positive corpus).")

    detector.threshold = threshold

    # Evaluate human samples (ground truth: clean/negative)
    fp = 0
    tn = 0
    for sample in human_samples:
        score = detector.score(sample)
        if score >= threshold:
            fp += 1
        else:
            tn += 1

    # Evaluate synthetic samples (ground truth: positive)
    tp = 0
    fn = 0
    for sample in synthetic_samples:
        score = detector.score(sample)
        if score >= threshold:
            tp += 1
        else:
            fn += 1

    total_h = len(human_samples)
    total_s = len(synthetic_samples)

    fpr = (fp / total_h) if total_h > 0 else 0.0
    tpr = (tp / total_s) if total_s > 0 else 0.0
    accuracy = ((tp + tn) / (total_h + total_s)) if (total_h + total_s) > 0 else 0.0

    precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = tpr
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return CalibrationEvaluation(
        threshold=threshold,
        total_human_samples=total_h,
        total_synthetic_samples=total_s,
        false_positive_rate=round(fpr, 4),
        true_positive_rate=round(tpr, 4),
        accuracy=round(accuracy, 4),
        f1_score=round(f1, 4),
    )


def run_parameter_sweep(
    detector: WatermarkAnalyzer | None = None,
    human_samples: list[str] | None = None,
    synthetic_samples: list[str] | None = None,
    threshold_range: list[float] | None = None,
) -> ParameterSweepResult:
    """Sweep detection thresholds across benchmark sets to determine optimal operating points."""
    if detector is None:
        detector = ClaudeWatermarkAnalyzer()
    if human_samples is None:
        human_samples = DEFAULT_HUMAN_SAMPLES
    if synthetic_samples is None:
        synthetic_samples = DEFAULT_SYNTHETIC_SAMPLES
    if threshold_range is None:
        threshold_range = [0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70]

    evaluations: list[CalibrationEvaluation] = []
    best_f1 = -1.0
    recommended_thresh = 0.35

    for th in threshold_range:
        res = evaluate_dataset(detector, human_samples, synthetic_samples, threshold=th)
        evaluations.append(res)
        if res.f1_score > best_f1:
            best_f1 = res.f1_score
            recommended_thresh = th

    return ParameterSweepResult(
        detector_name=detector.name,
        thresholds_evaluated=threshold_range,
        evaluations=evaluations,
        recommended_threshold=recommended_thresh,
        notes="Empirically calibrated threshold sweep across representative baseline corpus.",
    )
