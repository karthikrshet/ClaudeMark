"""Markdown report formatter for ClaudeMark."""

from __future__ import annotations

from ..core.diff import ForensicDiffResult
from ..core.text_stats import TextStatistics
from ..core.unicode_forensics import UnicodeForensicReport
from ..watermark.base import WatermarkResult


def format_markdown_report(
    source_name: str,
    stats: TextStatistics,
    unicode_rep: UnicodeForensicReport,
    wm_res: WatermarkResult,
    verbose: bool = False,
) -> str:
    """Format analysis as a GitHub-flavored Markdown report."""
    conf_pct = int(wm_res.confidence * 100)
    score_pct = int(wm_res.signal_score * 100)
    
    status_emoji = "🔍" if wm_res.status == "potential_signal" else ("⚠️" if wm_res.status == "strong_signal" else "✅")

    md = [
        f"# ClaudeMark Analysis Report: `{source_name}`",
        "",
        f"> **Summary**: {status_emoji} **{wm_res.status.upper().replace('_', ' ')}** — Signal Score: **{wm_res.signal_score:.2f}** ({score_pct}%) with **{conf_pct}%** confidence.",
        "",
        "## 1. Text Surface & Lexical Statistics",
        "",
        "| Metric | Value | Metric | Value |",
        "| :--- | :--- | :--- | :--- |",
        f"| **Characters** | {stats.characters:,} | **Unique Words** | {stats.unique_words:,} |",
        f"| **Characters (No Spaces)** | {stats.characters_no_spaces:,} | **Sentences** | {stats.sentences:,} |",
        f"| **Words** | {stats.words:,} | **Paragraphs** | {stats.paragraphs:,} |",
        f"| **Type-Token Ratio (TTR)** | {stats.type_token_ratio:.3f} | **Avg Sentence Length** | {stats.avg_sentence_length_words:.1f} words |",
        f"| **Word Entropy** | {stats.word_entropy:.2f} bits | **Hapax Legomena Ratio** | {stats.hapax_ratio:.3f} |",
        "",
        "## 2. Unicode Forensics & Invisible Characters",
        "",
        f"- **Anomalies Detected**: `{'YES' if unicode_rep.has_anomalies else 'NO'}` (Total: **{unicode_rep.total_anomalies}**)",
        f"- **Zero-Width Characters**: `{unicode_rep.zero_width_count}`",
        f"- **Control Characters**: `{unicode_rep.control_char_count}`",
        f"- **Non-Breaking Spaces (NBSP)**: `{unicode_rep.nbsp_count}`",
        f"- **Special / Exotic Spaces**: `{unicode_rep.special_space_count}`",
        f"- **BiDi Directional Overrides**: `{unicode_rep.bidi_control_count}`",
        f"- **BOM Header**: `{'Present' if unicode_rep.bom_present else 'None'}`",
        f"- **Canonical Normalization**: NFC (`{unicode_rep.is_nfc}`), NFKC (`{unicode_rep.is_nfkc}`)",
    ]

    if unicode_rep.findings:
        md.extend([
            "",
            "### Detailed Anomaly Breakdown",
            "",
            "| Codepoint | Description | Count | Category |",
            "| :--- | :--- | :--- | :--- |",
        ])
        for f in unicode_rep.findings:
            md.append(f"| `{f.codepoint}` | {f.name} | {f.count} | `{f.category}` |")

    md.extend([
        "",
        "## 3. Statistical AI Watermark Analysis",
        "",
        f"- **Algorithm**: `{wm_res.algorithm_name}` (v{wm_res.algorithm_version})",
        f"- **Signal Score**: **{wm_res.signal_score:.2f}** (Threshold: {wm_res.threshold:.2f})",
        f"- **Confidence**: **{conf_pct}%**",
        f"- **Interpretation**: {wm_res.interpretation}",
    ])

    if verbose and wm_res.hypothesis:
        md.extend([
            "",
            "### Hypothesis Testing",
            "",
            f"- **Null Hypothesis ($H_0$)**: {wm_res.hypothesis.null_hypothesis}",
            f"- **Alternative Hypothesis ($H_1$)**: {wm_res.hypothesis.alternative_hypothesis}",
            f"- **Test Statistic**: `{wm_res.hypothesis.test_statistic_name}` = `{wm_res.hypothesis.test_statistic_value:.4f}`",
            f"- **P-Value**: `{wm_res.hypothesis.p_value if wm_res.hypothesis.p_value is not None else 'N/A'}`",
            f"- **Interpretation**: {wm_res.hypothesis.confidence_interpretation}",
        ])

    md.extend([
        "",
        "## 4. Limitations & Research Disclaimers",
        "",
    ])
    for lim in wm_res.limitations:
        md.append(f"- {lim}")

    return "\n".join(md)
