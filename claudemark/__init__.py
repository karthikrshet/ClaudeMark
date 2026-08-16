"""ClaudeMark: Multi-AI Watermark & Provenance Forensics Toolkit.

A scientific, production-quality open-source toolkit for statistical AI watermark
analysis, Unicode steganography forensics, document cleaning, and C2PA / EXIF provenance.
"""

from __future__ import annotations

from typing import Any

from .core.diff import ForensicDiffResult, compute_forensic_diff
from .core.normalizer import NormalizationOptions, NormalizationResult, normalize_text
from .core.text_stats import TextStatistics, analyze_text_statistics
from .core.unicode_forensics import (
    AnomalyDetail,
    UnicodeForensicReport,
    analyze_unicode_forensics,
)
from .detectors.base import DetectionResult, StatisticalHypothesis, WatermarkDetector
from .detectors.claude import ClaudeWatermarkDetector
from .detectors.generic import GenericEntropyDetector
from .detectors.kirchenbauer import KirchenbauerDetector
from .detectors.registry import DetectorRegistry, detector_registry
from .detectors.synthid import SynthIDDetector
from .provenance.base import (
    BatchProcessSummary,
    FileCleaningReport,
    ProvenanceInspectionReport,
)
from .provenance.batch import (
    batch_clean,
    batch_inspect,
    clean_single_file,
    inspect_single_file,
)
from .watermark.base import WatermarkAnalyzer, WatermarkResult
from .watermark.claude_detector import ClaudeWatermarkAnalyzer
from .watermark.registry import registry

__version__ = "2.0.0"
__author__ = "Karthik R Shet"


def analyze_text(
    text: str,
    detector_name: str | None = None,
    threshold: float | None = None,
) -> dict[str, Any]:
    """High-level one-shot analysis returning text statistics, Unicode forensics,
    and statistical watermark evaluation.
    """
    stats = analyze_text_statistics(text)
    unicode_rep = analyze_unicode_forensics(text)
    
    detector = detector_registry.get(detector_name)
    if threshold is not None:
        detector.threshold = threshold
        
    wm_res = detector.detect(text)
    
    return {
        "text_statistics": stats,
        "unicode_forensics": unicode_rep,
        "watermark_result": wm_res,
    }


__all__ = [
    "__version__",
    "__author__",
    "analyze_text",
    "normalize_text",
    "compute_forensic_diff",
    "analyze_text_statistics",
    "analyze_unicode_forensics",
    "inspect_single_file",
    "clean_single_file",
    "batch_inspect",
    "batch_clean",
    "TextStatistics",
    "UnicodeForensicReport",
    "AnomalyDetail",
    "NormalizationOptions",
    "NormalizationResult",
    "ForensicDiffResult",
    "ProvenanceInspectionReport",
    "FileCleaningReport",
    "BatchProcessSummary",
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
