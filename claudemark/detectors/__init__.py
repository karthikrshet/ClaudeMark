"""ClaudeMark pluggable detector subpackage."""

from .base import DetectionResult, StatisticalHypothesis, WatermarkDetector
from .claude import ClaudeWatermarkDetector
from .generic import GenericEntropyDetector
from .kirchenbauer import KirchenbauerDetector
from .registry import DetectorRegistry, detector_registry
from .synthid import SynthIDDetector

__all__ = [
    "WatermarkDetector",
    "DetectionResult",
    "StatisticalHypothesis",
    "ClaudeWatermarkDetector",
    "KirchenbauerDetector",
    "SynthIDDetector",
    "GenericEntropyDetector",
    "DetectorRegistry",
    "detector_registry",
]
