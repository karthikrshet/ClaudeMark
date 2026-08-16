#!/usr/bin/env python3
"""Automated calibration baseline runner for ClaudeMark research."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from claudemark.watermark.experimental import run_parameter_sweep
from claudemark.watermark.registry import registry


def load_corpus_from_dir(dir_path: str) -> list[str]:
    """Load all text files from a directory."""
    p = Path(dir_path).resolve()
    if not p.is_dir():
        return []
    samples = []
    for f in p.glob("**/*"):
        if f.is_file() and f.suffix.lower() in (".txt", ".md", ".json"):
            try:
                content = f.read_text(encoding="utf-8", errors="replace").strip()
                if len(content) > 50:
                    samples.append(content)
            except Exception:
                pass
    return samples


def main() -> int:
    parser = argparse.ArgumentParser(description="ClaudeMark Benchmark Calibration Runner")
    parser.add_argument("--human", default="benchmarks/human", help="Directory with human-written text")
    parser.add_argument("--synthetic", default="benchmarks/synthetic", help="Directory with model-generated text")
    parser.add_argument("--algorithm", "-a", default="claude", help="Detector algorithm to evaluate")
    args = parser.parse_args()

    human_samples = load_corpus_from_dir(args.human)
    synth_samples = load_corpus_from_dir(args.synthetic)

    detector = registry.get(args.algorithm)

    print(f"ClaudeMark Calibration Benchmark: {detector.name}")
    print(f"Human samples loaded: {len(human_samples)} | Synthetic samples loaded: {len(synth_samples)}")

    if not human_samples and not synth_samples:
        print("\nNotice: No local dataset files found in benchmark directories.")
        print("Running synthetic test sweep on built-in baseline distributions...")
        human_samples = [
            "The historical records of early typography show that movable type revolutionized information sharing across continents.",
            "In botany, the vascular system of plants transports water and essential minerals from roots to the upper foliage.",
        ]
        synth_samples = [
            "In conclusion, it is important to analyze the implications of modern technologies. Furthermore, stakeholders must collaborate.",
            "Therefore, comprehensive systems are vital for optimizing organizational workflows across all enterprise domains.",
        ]

    result = run_parameter_sweep(
        detector=detector,
        human_samples=human_samples,
        synthetic_samples=synth_samples,
    )

    print("\nCalibration Results Table:")
    print("=" * 60)
    print(f"{'Threshold':<10} | {'F1-Score':<10} | {'FPR':<10} | {'TPR':<10} | {'Accuracy':<10}")
    print("-" * 60)
    for ev in result.evaluations:
        print(f"{ev.threshold:<10.2f} | {ev.f1_score:<10.2f} | {ev.false_positive_rate:<10.2f} | {ev.true_positive_rate:<10.2f} | {ev.accuracy:<10.2f}")
    print("=" * 60)
    print(f"Recommended Threshold for minimal FPR: {result.recommended_threshold:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
