"""Terminal ASCII formatter for ClaudeMark reports."""

from __future__ import annotations

from typing import Any

from ..core.diff import ForensicDiffResult
from ..core.text_stats import TextStatistics
from ..core.unicode_forensics import UnicodeForensicReport
from ..watermark.base import WatermarkResult


def format_terminal_report(
    source_name: str,
    stats: TextStatistics,
    unicode_rep: UnicodeForensicReport,
    wm_res: WatermarkResult,
    verbose: bool = False,
) -> str:
    """Format full analysis into a clean, human-readable terminal report."""
    conf_pct = int(wm_res.confidence * 100)
    score_pct = int(wm_res.signal_score * 100)
    
    # Visual gauge bar (20 chars wide)
    filled_blocks = int(round(wm_res.signal_score * 20))
    gauge = "█" * filled_blocks + "░" * (20 - filled_blocks)

    lines = [
        "ClaudeMark Analysis Report",
        "═" * 60,
        f"Source: {source_name}",
        "",
        "Text Statistics",
        "─" * 30,
        f"Characters:        {stats.characters:,}",
        f"Characters (no sp):{stats.characters_no_spaces:,}",
        f"Words:             {stats.words:,} (Unique: {stats.unique_words:,})",
        f"Sentences:         {stats.sentences:,}",
        f"Paragraphs:        {stats.paragraphs:,}",
        f"Avg Sentence Len:  {stats.avg_sentence_length_words:.1f} words",
        f"Lexical Richness:  TTR={stats.type_token_ratio:.3f}, Hapax={stats.hapax_ratio:.3f}",
        f"Shannon Entropy:   {stats.word_entropy:.2f} bits (word), {stats.char_entropy:.2f} bits (char)",
        "",
        "Unicode Forensics",
        "─" * 30,
        f"Zero-width chars:  {unicode_rep.zero_width_count}",
        f"Control chars:     {unicode_rep.control_char_count}",
        f"NBSP characters:   {unicode_rep.nbsp_count}",
        f"Special spaces:    {unicode_rep.special_space_count}",
        f"BiDi overrides:    {unicode_rep.bidi_control_count}",
        f"BOM Header:        {'YES' if unicode_rep.bom_present else 'NO'}",
        f"Normalization:     NFC: {'YES' if unicode_rep.is_nfc else 'NO'} | NFKC: {'YES' if unicode_rep.is_nfkc else 'NO'}",
    ]

    if unicode_rep.findings:
        lines.append("")
        lines.append("Detected Anomalies:")
        for f in unicode_rep.findings:
            lines.append(f"  • {f.codepoint} {f.name} × {f.count}")

    lines.extend([
        "",
        "Statistical Watermark Analysis",
        "─" * 30,
        f"Signal Score:      {wm_res.signal_score:.2f} [{gauge}] {score_pct}%",
        f"Confidence:        {conf_pct}%",
        f"Status:            {wm_res.status.upper().replace('_', ' ')}",
        f"Analyzer:          {wm_res.algorithm_name} v{wm_res.algorithm_version}",
        "",
        f"Interpretation:    {wm_res.interpretation}",
    ])

    if verbose and wm_res.hypothesis:
        lines.extend([
            "",
            "Statistical Hypothesis Testing",
            "─" * 30,
            f"Null Hypothesis:   {wm_res.hypothesis.null_hypothesis}",
            f"Alt Hypothesis:    {wm_res.hypothesis.alternative_hypothesis}",
            f"Test Statistic:    {wm_res.hypothesis.test_statistic_name} = {wm_res.hypothesis.test_statistic_value:.4f}",
            f"P-Value:           {wm_res.hypothesis.p_value if wm_res.hypothesis.p_value is not None else 'N/A'}",
            f"Interpretation:    {wm_res.hypothesis.confidence_interpretation}",
        ])

    lines.extend([
        "",
        "Important Limitations & Disclaimer",
        "─" * 30,
    ])
    for lim in wm_res.limitations:
        lines.append(f"  * {lim}")

    return "\n".join(lines)


def format_terminal_diff(diff: ForensicDiffResult, original_name: str, new_name: str) -> str:
    """Format forensic text comparison into a terminal report."""
    lines = [
        "ClaudeMark Forensic Diff",
        "═" * 60,
        f"Original: {original_name} | Processed: {new_name}",
        "",
        "Comparative Forensics",
        "─" * 30,
        f"Characters:          Original: {diff.original_chars:,} | New: {diff.new_chars:,} (delta: {diff.char_delta:+d}, {diff.char_change_pct}%)",
        f"Words:               Original: {diff.original_words:,} | New: {diff.new_words:,} (delta: {diff.word_delta:+d})",
        f"Unicode Anomalies:   Original: {diff.original_unicode_anomalies} | New: {diff.new_unicode_anomalies} (removed: {diff.anomalies_removed})",
        f"Visible Text Change: {diff.visible_difference_pct}% (similarity: {round(diff.visible_similarity_ratio * 100, 2)}%)",
    ]
    if diff.original_signal_score > 0.0 or diff.new_signal_score > 0.0:
        lines.append(
            f"Statistical Score:   Original: {diff.original_signal_score:.2f} | New: {diff.new_signal_score:.2f} (delta: {diff.score_delta:+.2f})"
        )
    return "\n".join(lines)
