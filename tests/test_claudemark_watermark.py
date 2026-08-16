"""Unit tests for ClaudeMark watermark detectors and statistical modeling."""

import pytest
from claudemark.watermark.base import WatermarkAnalyzer
from claudemark.watermark.claude_detector import ClaudeWatermarkAnalyzer
from claudemark.watermark.experimental import evaluate_dataset, run_parameter_sweep
from claudemark.watermark.registry import DetectorRegistry, registry
from claudemark.watermark.statistical import (
    compute_burstiness,
    compute_shannon_entropy,
    compute_yules_k,
    z_to_p_value,
)


def test_statistical_functions():
    items = ["a", "b", "c", "d"]
    ent = compute_shannon_entropy(items)
    assert ent == 2.0  # log2(4) = 2.0 bits

    # Burstiness
    lengths = [10, 10, 10, 10]
    b_uniform = compute_burstiness(lengths)
    assert b_uniform == -1.0  # Perfectly uniform

    lengths_varied = [2, 25, 4, 30]
    b_varied = compute_burstiness(lengths_varied)
    assert b_varied > -1.0

    # Yule's K
    words = ["the", "the", "the", "fox"]
    k = compute_yules_k(words)
    assert k > 0.0

    # P-value from z-score
    p = z_to_p_value(0.0)
    assert abs(p - 1.0) < 1e-4
    p_high_z = z_to_p_value(3.0)
    assert p_high_z < 0.01


def test_claude_watermark_analyzer_short_text():
    detector = ClaudeWatermarkAnalyzer()
    res = detector.analyze("Hi there.")
    assert res.signal_score == 0.0
    assert res.status == "clean_or_low_signal"
    assert "too short" in res.interpretation.lower() or "insufficient" in res.interpretation.lower()


def test_claude_watermark_analyzer_normal_prose():
    detector = ClaudeWatermarkAnalyzer(threshold=0.65)
    text = (
        "In the early Renaissance, Italian artists developed mathematical perspective. "
        "Brunelleschi demonstrated linear perspective in Florence using mirrors. "
        "Later, Leonardo da Vinci expanded on atmospheric perspective in his notebooks, "
        "revolutionizing Western visual arts for centuries to come."
    )
    res = detector.analyze(text)
    assert 0.0 <= res.signal_score <= 1.0
    assert 0.0 <= res.confidence <= 1.0
    assert res.hypothesis is not None
    assert res.hypothesis.test_statistic_name == "Composite Deviation Z-Score"
    assert len(res.limitations) >= 2


def test_detector_registry():
    reg = DetectorRegistry()
    assert "claude" in reg.list_detectors()
    assert "entropy-burstiness" in reg.list_detectors()
    
    det = reg.get("claude")
    assert isinstance(det, ClaudeWatermarkAnalyzer)

    with pytest.raises(KeyError):
        reg.get("non_existent_detector")


def test_experimental_evaluation_and_sweep():
    detector = ClaudeWatermarkAnalyzer()
    human = ["This is a standard natural human paragraph discussing local historical events."]
    synth = ["In conclusion, it is important to analyze comprehensive paradigms across stakeholders."]
    
    eval_res = evaluate_dataset(detector, human, synth, threshold=0.60)
    assert 0.0 <= eval_res.accuracy <= 1.0
    assert 0.0 <= eval_res.false_positive_rate <= 1.0
    
    sweep = run_parameter_sweep(detector, human, synth, threshold_range=[0.5, 0.7])
    assert len(sweep.evaluations) == 2
    assert sweep.recommended_threshold in [0.5, 0.7]
