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


def render_html_diff(
    original_text: str,
    processed_text: str,
    file1_name: str = "Original",
    file2_name: str = "Processed",
    diff_result: ForensicDiffResult | None = None,
) -> str:
    """Render an interactive side-by-side dark-mode HTML comparison report."""
    if diff_result is None:
        diff_result = compute_forensic_diff(original_text, processed_text)

    html_diff = difflib.HtmlDiff(tabsize=4, wrapcolumn=60)
    diff_table = html_diff.make_table(
        original_text.splitlines(),
        processed_text.splitlines(),
        fromdesc=file1_name,
        todesc=file2_name,
        context=True,
        numlines=3,
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ClaudeMark Forensic Diff: {file1_name} vs {file2_name}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; background: #0f172a; color: #e2e8f0; margin: 0; padding: 24px; }}
  .header {{ border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; }}
  h1 {{ margin: 0 0 8px; color: #38bdf8; font-size: 24px; }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .card {{ background: #1e293b; padding: 16px; border-radius: 8px; border: 1px solid #334155; }}
  .card-label {{ color: #94a3b8; font-size: 12px; text-transform: uppercase; margin-bottom: 4px; }}
  .card-val {{ font-size: 20px; font-weight: bold; color: #f8fafc; }}
  .diff-wrapper {{ background: #1e293b; border-radius: 8px; padding: 16px; overflow-x: auto; border: 1px solid #334155; }}
  table.diff {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  table.diff td {{ padding: 4px 8px; font-family: monospace; }}
  .diff_header {{ background: #0f172a; color: #64748b; font-weight: bold; }}
  .diff_next {{ display: none; }}
  .diff_add {{ background: #064e3b; color: #6ee7b7; }}
  .diff_chg {{ background: #713f12; color: #fde047; }}
  .diff_sub {{ background: #7f1d1d; color: #fca5a5; }}
</style>
</head>
<body>
<div class="header">
  <h1>ClaudeMark Forensic Comparison Report</h1>
  <div>Comparing: <code>{file1_name}</code> vs <code>{file2_name}</code></div>
</div>
<div class="stats-grid">
  <div class="card"><div class="card-label">Visible Similarity</div><div class="card-val">{round(diff_result.visible_similarity_ratio * 100.0, 1)}%</div></div>
  <div class="card"><div class="card-label">Unicode Anomalies Removed</div><div class="card-val">{diff_result.anomalies_removed}</div></div>
  <div class="card"><div class="card-label">Character Delta</div><div class="card-val">{diff_result.char_delta:+d} ({diff_result.char_change_pct}%)</div></div>
  <div class="card"><div class="card-label">Word Delta</div><div class="card-val">{diff_result.word_delta:+d}</div></div>
</div>
<div class="diff-wrapper">
  {diff_table}
</div>
</body>
</html>
"""
