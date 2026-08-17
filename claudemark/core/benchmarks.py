"""Reproducible Scientific Benchmark Engine for ClaudeMark.

Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

from ..detectors.registry import detector_registry


BENCHMARK_SAMPLES = [
    # Clean text
    {"text": "The quick brown fox jumps over the lazy dog under the bright morning sun.", "is_watermarked": False, "has_unicode": False},
    {"text": "A standard historical analysis demonstrates significant societal transitions across the Mediterranean region during late antiquity.", "is_watermarked": False, "has_unicode": False},
    {"text": "Photosynthesis is the biological process by which green plants synthesize nutrients from carbon dioxide and water using radiant sunlight.", "is_watermarked": False, "has_unicode": False},
    
    # Statistical watermark regularities
    {"text": "In conclusion, comprehensive strategic paradigms are fundamentally essential for optimizing interdisciplinary synergies and transformative outcomes.", "is_watermarked": True, "has_unicode": False},
    {"text": "Furthermore, it is imperative to recognize that multifaceted methodologies facilitate holistic alignment across contemporary operational dynamics.", "is_watermarked": True, "has_unicode": False},
    {"text": "Consequently, structured frameworks serve as indispensable conduits for orchestrating scalable and sustainable infrastructure modernizations.", "is_watermarked": True, "has_unicode": False},

    # Zero-width Unicode steganography
    {"text": "This document contains\u200b hidden zero-width spaces\u200c embedded inside the words.", "is_watermarked": False, "has_unicode": True},
    {"text": "Encrypted prompt injection payload \u202e\u200bhidden inside plain text message.", "is_watermarked": False, "has_unicode": True},
]


@dataclass
class BenchmarkMetric:
    detector_name: str
    total_samples: int
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    accuracy: float


@dataclass
class BenchmarkSuiteResult:
    version: str = "2.1.0"
    total_samples: int = len(BENCHMARK_SAMPLES)
    metrics: list[BenchmarkMetric] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_benchmark_suite(reproduce: bool = True) -> BenchmarkSuiteResult:
    """Execute reproducible detector evaluation across synthetic benchmark corpus."""
    result = BenchmarkSuiteResult()
    
    for det_name in detector_registry.list_detectors():
        detector = detector_registry.get(det_name)
        tp = tn = fp = fn = 0

        for sample in BENCHMARK_SAMPLES:
            res = detector.detect(sample["text"])
            actual = sample["is_watermarked"]
            predicted = res.is_watermarked

            if actual and predicted:
                tp += 1
            elif not actual and not predicted:
                tn += 1
            elif not actual and predicted:
                fp += 1
            elif actual and not predicted:
                fn += 1

        total = len(BENCHMARK_SAMPLES)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        acc = (tp + tn) / total if total > 0 else 0.0

        result.metrics.append(BenchmarkMetric(
            detector_name=det_name,
            total_samples=total,
            true_positives=tp,
            true_negatives=tn,
            false_positives=fp,
            false_negatives=fn,
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1, 4),
            accuracy=round(acc, 4),
        ))

    return result


def print_benchmark_table(result: BenchmarkSuiteResult) -> None:
    """Pretty-print benchmark results table."""
    print("ClaudeMark Reproducible Benchmark Suite Matrix (v2.1.0)")
    print("═" * 75)
    print(f"{'Detector':<16} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
    print("─" * 75)
    for m in result.metrics:
        print(f"{m.detector_name:<16} | {m.accuracy:<10.2f} | {m.precision:<10.2f} | {m.recall:<10.2f} | {m.f1_score:<10.2f}")
    print("═" * 75)
