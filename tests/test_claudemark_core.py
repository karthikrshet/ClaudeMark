"""Unit tests for ClaudeMark core analysis, Unicode forensics, normalizer, and diff."""

import pytest
from claudemark.core.diff import compute_forensic_diff
from claudemark.core.normalizer import NormalizationOptions, normalize_text
from claudemark.core.text_stats import analyze_text_statistics
from claudemark.core.unicode_forensics import analyze_unicode_forensics


def test_text_statistics_empty():
    stats = analyze_text_statistics("")
    assert stats.characters == 0
    assert stats.words == 0
    assert stats.sentences == 0


def test_text_statistics_basic_prose():
    text = "The quick brown fox jumps over the lazy dog. It was a sunny day."
    stats = analyze_text_statistics(text)
    assert stats.characters == len(text)
    assert stats.words == 14
    assert stats.sentences == 2
    assert stats.paragraphs == 1
    assert stats.type_token_ratio > 0.7
    assert stats.char_entropy > 0.0
    assert stats.word_entropy > 0.0
    assert stats.punctuation.period_count == 2


def test_unicode_forensics_clean_text():
    text = "Clean standard English prose without hidden characters."
    rep = analyze_unicode_forensics(text)
    assert not rep.has_anomalies
    assert rep.zero_width_count == 0
    assert rep.nbsp_count == 0
    assert rep.is_nfc
    assert rep.summary_text == "Clean (No Unicode anomalies detected)"


def test_unicode_forensics_detects_zero_width_and_bom():
    text = "\ufeffHello\u200bworld\u200ctest\u200dmark\u00a0here."
    rep = analyze_unicode_forensics(text)
    assert rep.has_anomalies
    assert rep.bom_present
    assert rep.zero_width_count == 4  # BOM + ZWSP + ZWNJ + ZWJ
    assert rep.nbsp_count == 1
    assert len(rep.findings) >= 4


def test_safe_normalization_preserves_plain_text():
    sample = "Regular sentence with numbers 123 and punctuation! Is it untouched? Yes."
    res = normalize_text(sample)
    assert res.normalized_text == sample
    assert res.characters_removed == 0


def test_safe_normalization_strips_invisible_watermarks():
    sample = "Secret\u200b\u200c\u200d\ufeff hidden\u00a0marks"
    res = normalize_text(sample)
    assert res.normalized_text == "Secret hidden marks"
    assert res.zero_width_removed == 4
    assert res.spaces_normalized == 1
    assert res.bom_removed


def test_forensic_diff_computes_accurate_deltas():
    orig = "Original\u200b text with 10 words and hidden zero-width marks here."
    proc = "Original text with 10 words and hidden zero-width marks here."
    diff = compute_forensic_diff(orig, proc, original_score=0.85, new_score=0.20)
    
    assert diff.original_chars > diff.new_chars
    assert diff.char_delta == -1
    assert diff.original_unicode_anomalies == 1
    assert diff.new_unicode_anomalies == 0
    assert diff.anomalies_removed == 1
    assert diff.score_delta == -0.65
    assert diff.visible_similarity_ratio > 0.95
