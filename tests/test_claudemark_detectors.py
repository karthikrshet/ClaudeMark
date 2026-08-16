"""Unit tests for ClaudeMark pluggable detector subpackage."""

import pytest
from claudemark.detectors.claude import ClaudeWatermarkDetector
from claudemark.detectors.generic import GenericEntropyDetector
from claudemark.detectors.kirchenbauer import KirchenbauerDetector
from claudemark.detectors.registry import DetectorRegistry, detector_registry
from claudemark.detectors.synthid import SynthIDDetector


def test_detector_registry_pluggable_engines():
    reg = DetectorRegistry()
    detectors = reg.list_detectors()
    assert "claude" in detectors
    assert "kirchenbauer" in detectors
    assert "synthid" in detectors
    assert "generic" in detectors


def test_kirchenbauer_detector_behavior():
    det = KirchenbauerDetector(gamma=0.5)
    text = "The rapid advancements in artificial intelligence have transformed modern software engineering practices."
    res = det.detect(text)
    assert res.algorithm_name == "Kirchenbauer Red/Green Statistical Detector"
    assert 0.0 <= res.signal_score <= 1.0
    assert res.hypothesis is not None
    assert "H0" in res.hypothesis.null_hypothesis
    assert "gamma" in res.features


def test_synthid_detector_behavior():
    det = SynthIDDetector()
    text = "In recent studies, researchers evaluated language model watermarking using entropy modulation techniques."
    res = det.detect(text)
    assert res.algorithm_name == "SynthID-Style Research Detector"
    assert 0.0 <= res.signal_score <= 1.0
    assert "entropy" in res.features


def test_generic_entropy_detector():
    det = GenericEntropyDetector()
    text = "Short sentence one. Short sentence two. Short sentence three."
    res = det.detect(text)
    assert 0.0 <= res.signal_score <= 1.0
    assert "burstiness" in res.features
