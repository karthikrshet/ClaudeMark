"""Tests for statistical watermark disruption, text restructuring, and evaluation."""

import pytest
from claudemark.rewrite.base import RewriteEvaluation, RewriteResult
from claudemark.rewrite.evaluation import evaluate_rewrite
from claudemark.rewrite.paraphrase import disrupt_watermark
from claudemark.rewrite.transforms import rebalance_cadence, substitute_synonyms


def test_substitute_synonyms():
    text = "Furthermore, it is essential to demonstrate this paradigm."
    transformed = substitute_synonyms(text, substitution_rate=1.0, seed=42)
    assert transformed != text
    assert len(transformed.split()) >= 5


def test_rebalance_cadence():
    text = "This is a document, which is important. It has multiple sentences."
    rebalanced = rebalance_cadence(text)
    assert ", which is" not in rebalanced
    assert "important" in rebalanced


def test_evaluate_rewrite():
    orig = "This is a test of the emergency broadcast system. Furthermore, it demonstrates comprehensive analysis."
    proc = "This is a test of the broadcast system. Moreover, it illustrates thorough analysis."
    ev = evaluate_rewrite(orig, proc, detector_name="claude")
    assert isinstance(ev, RewriteEvaluation)
    assert 0.0 <= ev.semantic_similarity <= 1.0
    assert ev.character_change_ratio >= 0.0
    assert ev.original_entropy > 0.0


def test_disrupt_watermark():
    text = "Furthermore, this is a crucial implementation of the paradigm. Moreover, we demonstrate it here."
    res = disrupt_watermark(text, strategy="synonym_cadence", detector_name="claude")
    assert isinstance(res, RewriteResult)
    assert res.success is True
    assert res.rewritten_text != ""
    assert res.evaluation is not None
    assert isinstance(res.to_dict(), dict)
