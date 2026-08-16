"""Forensic difference and comparative analysis module for ClaudeMark."""

from __future__ import annotations

import difflib
from dataclasses import asdict, dataclass
from typing import Any

from .text_stats import analyze_text_statistics
from .unicode_forensics import analyze_unicode_forensics


@dataclass
class ForensicDiffResult:
    original_chars: int
    new_chars: int
    char_delta: int
    char_change_pct: float
    
    original_words: int
    new_words: int
    word_delta: int
    
    original_unicode_anomalies: int
    new_unicode_anomalies: int
    anomalies_removed: int
    
    visible_similarity_ratio: float
    visible_difference_pct: float
    
    original_signal_score: float = 0.0
    new_signal_score: float = 0.0
    score_delta: float = 0.0
    
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_forensic_diff(
    original_text: str,
    processed_text: str,
    original_score: float = 0.0,
    new_score: float = 0.0,
) -> ForensicDiffResult:
    """Compute a detailed forensic comparison between an original and processed text."""
    orig_stats = analyze_text_statistics(original_text)
    new_stats = analyze_text_statistics(processed_text)
    
    orig_u = analyze_unicode_forensics(original_text)
    new_u = analyze_unicode_forensics(processed_text)
    
    # Calculate similarity ratio using SequenceMatcher
    matcher = difflib.SequenceMatcher(None, original_text, processed_text)
    similarity = matcher.ratio()
    diff_pct = round((1.0 - similarity) * 100.0, 2)
    
    char_delta = new_stats.characters - orig_stats.characters
    char_change_pct = round((abs(char_delta) / orig_stats.characters * 100.0), 2) if orig_stats.characters > 0 else 0.0
    word_delta = new_stats.words - orig_stats.words
    
    anomalies_removed = max(0, orig_u.total_anomalies - new_u.total_anomalies)
    score_delta = round(new_score - original_score, 4)

    summary_lines = [
        f"Characters: {orig_stats.characters:,} -> {new_stats.characters:,} (delta: {char_delta:+d})",
        f"Unicode anomalies: {orig_u.total_anomalies} -> {new_u.total_anomalies} (removed: {anomalies_removed})",
        f"Visible text difference: {diff_pct}% (similarity: {round(similarity * 100.0, 2)}%)",
    ]
    if original_score > 0.0 or new_score > 0.0:
        summary_lines.append(f"Statistical score: {original_score:.2f} -> {new_score:.2f} (delta: {score_delta:+.2f})")

    return ForensicDiffResult(
        original_chars=orig_stats.characters,
        new_chars=new_stats.characters,
        char_delta=char_delta,
        char_change_pct=char_change_pct,
        original_words=orig_stats.words,
        new_words=new_stats.words,
        word_delta=word_delta,
        original_unicode_anomalies=orig_u.total_anomalies,
        new_unicode_anomalies=new_u.total_anomalies,
        anomalies_removed=anomalies_removed,
        visible_similarity_ratio=round(similarity, 4),
        visible_difference_pct=diff_pct,
        original_signal_score=original_score,
        new_signal_score=new_score,
        score_delta=score_delta,
        summary="\n".join(summary_lines),
    )
