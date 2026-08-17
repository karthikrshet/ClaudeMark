"""JSON report formatter for ClaudeMark."""

from __future__ import annotations

import json
from typing import Any

from .. import __version__ as VERSION
from ..core.text_stats import TextStatistics
from ..core.unicode_forensics import UnicodeForensicReport
from ..watermark.base import WatermarkResult


def format_json_report(
    stats: TextStatistics,
    unicode_rep: UnicodeForensicReport,
    wm_res: WatermarkResult,
    source_name: str = "input_text",
    indent: int = 2,
) -> str:
    """Construct structured, machine-readable JSON report."""
    payload = {
        "tool": "ClaudeMark",
        "version": VERSION,
        "source": source_name,
        "input": {
            "characters": stats.characters,
            "characters_no_spaces": stats.characters_no_spaces,
            "words": stats.words,
            "unique_words": stats.unique_words,
            "sentences": stats.sentences,
            "paragraphs": stats.paragraphs,
            "lines": stats.lines,
        },
        "unicode_forensics": {
            "has_anomalies": unicode_rep.has_anomalies,
            "total_anomalies": unicode_rep.total_anomalies,
            "zero_width": unicode_rep.zero_width_count,
            "control_characters": unicode_rep.control_char_count,
            "nbsp": unicode_rep.nbsp_count,
            "special_spaces": unicode_rep.special_space_count,
            "bidi_controls": unicode_rep.bidi_control_count,
            "bom_present": unicode_rep.bom_present,
            "homoglyphs": unicode_rep.homoglyph_count,
            "normalization": {
                "is_nfc": unicode_rep.is_nfc,
                "is_nfkc": unicode_rep.is_nfkc,
                "is_nfd": unicode_rep.is_nfd,
                "is_nfkd": unicode_rep.is_nfkd,
            },
            "findings": [f.to_dict() if hasattr(f, "to_dict") else vars(f) for f in unicode_rep.findings],
        },
        "text_statistics": stats.to_dict(),
        "watermark_analysis": {
            "algorithm": wm_res.algorithm_name,
            "algorithm_version": wm_res.algorithm_version,
            "signal_score": wm_res.signal_score,
            "confidence": wm_res.confidence,
            "status": wm_res.status,
            "threshold": wm_res.threshold,
            "interpretation": wm_res.interpretation,
            "features": wm_res.features,
            "hypothesis": wm_res.hypothesis.to_dict() if wm_res.hypothesis else None,
        },
        "limitations": wm_res.limitations,
    }
    return json.dumps(payload, ensure_ascii=False, indent=indent)
