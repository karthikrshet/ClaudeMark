"""Experimental calibration and parameter sweep tools for ClaudeMark research."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .base import WatermarkAnalyzer
from .claude_detector import ClaudeWatermarkAnalyzer


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
    threshold: float = 0.65,
) -> CalibrationEvaluation:
    """Evaluate detector performance across human and synthetic text corpora."""
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
        human_samples = []
    if synthetic_samples is None:
        synthetic_samples = []
    if threshold_range is None:
        threshold_range = [0.40, 0.50, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]

    evaluations: list[CalibrationEvaluation] = []
    best_f1 = -1.0
    recommended_thresh = 0.65

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
        notes="Experimental threshold sweep for research benchmarking.",
    )
