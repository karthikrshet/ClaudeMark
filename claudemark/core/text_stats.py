"""Text statistics and distribution analysis module for ClaudeMark."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PunctuationStats:
    total: int = 0
    frequency_per_1k_words: float = 0.0
    period_count: int = 0
    comma_count: int = 0
    semicolon_count: int = 0
    colon_count: int = 0
    dash_count: int = 0
    hyphen_count: int = 0
    quote_count: int = 0
    parenthesis_count: int = 0
    exclamation_count: int = 0
    question_count: int = 0


@dataclass
class TextStatistics:
    characters: int = 0
    characters_no_spaces: int = 0
    words: int = 0
    unique_words: int = 0
    sentences: int = 0
    paragraphs: int = 0
    lines: int = 0
    
    # Lexical richness
    type_token_ratio: float = 0.0  # TTR = unique / total words
    hapax_legomena_count: int = 0  # words occurring exactly once
    hapax_ratio: float = 0.0
    
    # Length distributions
    avg_word_length: float = 0.0
    avg_sentence_length_words: float = 0.0
    avg_sentence_length_chars: float = 0.0
    sentence_length_variance: float = 0.0
    sentence_length_std_dev: float = 0.0
    
    # Entropy & repetition
    char_entropy: float = 0.0
    word_entropy: float = 0.0
    repetition_rate: float = 0.0
    
    # Sub-statistics
    punctuation: PunctuationStats = field(default_factory=PunctuationStats)
    top_words: list[tuple[str, int]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_WORD_RE = re.compile(r"\b[^\W\d_]+(?:'[^\W\d_]+)?\b", re.UNICODE)


def _segment_sentences(text: str) -> list[str]:
    """Linearly segment text into sentences with O(n) complexity and zero backtracking."""
    sentences: list[str] = []
    current: list[str] = []
    for char in text:
        current.append(char)
        if char in ".!?" and len(current) > 1:
            s = "".join(current).strip()
            if s:
                sentences.append(s)
            current = []
    if current:
        rest = "".join(current).strip()
        if rest:
            sentences.append(rest)
    return sentences


def calculate_entropy(elements: list[Any]) -> float:
    """Compute Shannon entropy in bits for a sequence of elements."""
    if not elements:
        return 0.0
    counts = Counter(elements)
    total = len(elements)
    return -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)


def analyze_text_statistics(text: str) -> TextStatistics:
    """Analyze surface and lexical statistical properties of input text."""
    if not text:
        return TextStatistics()

    char_count = len(text)
    char_no_spaces = len(re.sub(r"\s+", "", text))
    
    # Paragraphs and lines
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    paragraph_count = max(1, len(paragraphs)) if text.strip() else 0
    lines = [line for line in text.splitlines() if line.strip()]
    line_count = len(lines)
    
    # Words
    words = _WORD_RE.findall(text.lower())
    word_count = len(words)
    word_counts = Counter(words)
    unique_words = len(word_counts)
    
    # Lexical Richness
    ttr = (unique_words / word_count) if word_count > 0 else 0.0
    hapax = sum(1 for w, c in word_counts.items() if c == 1)
    hapax_ratio = (hapax / word_count) if word_count > 0 else 0.0
    
    # Word lengths
    avg_word_len = (sum(len(w) for w in words) / word_count) if word_count > 0 else 0.0
    
    # Sentences
    raw_sentences: list[str] = []
    for para in paragraphs:
        for s in _segment_sentences(para):
            cleaned = s.strip()
            if cleaned:
                raw_sentences.append(cleaned)
                
    sentence_count = len(raw_sentences) if raw_sentences else (1 if word_count > 0 else 0)
    
    # Sentence length metrics (in words)
    sentence_lengths = [len(_WORD_RE.findall(s)) for s in raw_sentences if s]
    if not sentence_lengths and word_count > 0:
        sentence_lengths = [word_count]
        
    if sentence_lengths:
        avg_sent_len_words = sum(sentence_lengths) / len(sentence_lengths)
        avg_sent_len_chars = char_count / len(sentence_lengths)
        sent_variance = sum((l - avg_sent_len_words) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        sent_std_dev = math.sqrt(sent_variance)
    else:
        avg_sent_len_words = 0.0
        avg_sent_len_chars = 0.0
        sent_variance = 0.0
        sent_std_dev = 0.0
        
    # Punctuation analysis
    punct_stats = PunctuationStats(
        period_count=text.count("."),
        comma_count=text.count(","),
        semicolon_count=text.count(";"),
        colon_count=text.count(":"),
        dash_count=text.count("—") + text.count("–"),
        hyphen_count=text.count("-"),
        quote_count=text.count('"') + text.count("'") + text.count("“") + text.count("”"),
        parenthesis_count=text.count("(") + text.count(")") + text.count("[") + text.count("]"),
        exclamation_count=text.count("!"),
        question_count=text.count("?"),
    )
    all_punct = sum([
        punct_stats.period_count,
        punct_stats.comma_count,
        punct_stats.semicolon_count,
        punct_stats.colon_count,
        punct_stats.dash_count,
        punct_stats.hyphen_count,
        punct_stats.quote_count,
        punct_stats.parenthesis_count,
        punct_stats.exclamation_count,
        punct_stats.question_count,
    ])
    punct_stats.total = all_punct
    punct_stats.frequency_per_1k_words = (all_punct / word_count * 1000) if word_count > 0 else 0.0
    
    # Entropy & repetition
    char_entropy = calculate_entropy(list(text))
    word_entropy = calculate_entropy(words)
    
    # 3-gram repetition rate
    if len(words) >= 3:
        trigrams = [tuple(words[i:i + 3]) for i in range(len(words) - 2)]
        trigram_counts = Counter(trigrams)
        repeated_trigrams = sum(c for c in trigram_counts.values() if c > 1)
        repetition_rate = repeated_trigrams / len(trigrams)
    else:
        repetition_rate = 0.0

    return TextStatistics(
        characters=char_count,
        characters_no_spaces=char_no_spaces,
        words=word_count,
        unique_words=unique_words,
        sentences=sentence_count,
        paragraphs=paragraph_count,
        lines=line_count,
        type_token_ratio=round(ttr, 4),
        hapax_legomena_count=hapax,
        hapax_ratio=round(hapax_ratio, 4),
        avg_word_length=round(avg_word_len, 2),
        avg_sentence_length_words=round(avg_sent_len_words, 2),
        avg_sentence_length_chars=round(avg_sent_len_chars, 2),
        sentence_length_variance=round(sent_variance, 2),
        sentence_length_std_dev=round(sent_std_dev, 2),
        char_entropy=round(char_entropy, 4),
        word_entropy=round(word_entropy, 4),
        repetition_rate=round(repetition_rate, 4),
        punctuation=punct_stats,
        top_words=word_counts.most_common(10),
    )
