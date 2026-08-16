"""ClaudeMark core analysis, forensics, normalization, and comparison subpackage."""

from .diff import ForensicDiffResult, compute_forensic_diff
from .normalizer import NormalizationOptions, NormalizationResult, normalize_text
from .text_stats import PunctuationStats, TextStatistics, analyze_text_statistics
from .unicode_forensics import (
    AnomalyDetail,
    UnicodeForensicReport,
    analyze_unicode_forensics,
)

__all__ = [
    "TextStatistics",
    "PunctuationStats",
    "analyze_text_statistics",
    "UnicodeForensicReport",
    "AnomalyDetail",
    "analyze_unicode_forensics",
    "NormalizationOptions",
    "NormalizationResult",
    "normalize_text",
    "ForensicDiffResult",
    "compute_forensic_diff",
]
