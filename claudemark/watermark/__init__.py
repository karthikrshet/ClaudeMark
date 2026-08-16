"""ClaudeMark watermark analysis, statistical models, and research detectors."""

from .base import StatisticalHypothesis, WatermarkAnalyzer, WatermarkResult
from .claude_detector import ClaudeWatermarkAnalyzer
from .experimental import (
    CalibrationEvaluation,
    ParameterSweepResult,
    evaluate_dataset,
    run_parameter_sweep,
)
from .registry import DetectorRegistry, EntropyBurstinessDetector, registry
from .statistical import (
    compute_burstiness,
    compute_ngram_entropy,
    compute_shannon_entropy,
    compute_token_transition_regularity,
    compute_yules_k,
    z_to_p_value,
)

__all__ = [
    "WatermarkAnalyzer",
    "WatermarkResult",
    "StatisticalHypothesis",
    "ClaudeWatermarkAnalyzer",
    "EntropyBurstinessDetector",
    "DetectorRegistry",
    "registry",
    "compute_burstiness",
    "compute_shannon_entropy",
    "compute_ngram_entropy",
    "compute_token_transition_regularity",
    "compute_yules_k",
    "z_to_p_value",
    "CalibrationEvaluation",
    "ParameterSweepResult",
    "evaluate_dataset",
    "run_parameter_sweep",
]
