# ClaudeMark Empirical Benchmark Suite

This directory contains evaluation harnesses and calibration tooling for measuring empirical True Positive Rates (TPR) and False Positive Rates (FPR) across diverse text distributions.

---

## 📊 Benchmark Calibration Methodology

Statistical watermarks operate on probabilistic distributions. To establish trustworthy detection thresholds without overfitting, detectors are evaluated across balanced corpora:

| Dataset Category | Description | Target Evaluation Metric |
| :--- | :--- | :--- |
| **Human Baseline** | Curated natural human prose (academic papers, journalism, Wikipedia, literature) | False Positive Rate (FPR) $\le 1.0\%$ |
| **Synthetic Baseline** | Unwatermarked model outputs (sampling from open & closed LLMs) | Neutral classification |
| **Watermarked Set** | Model outputs generated under specific watermark constraints | True Positive Rate (TPR) $\ge 90.0\%$ |

---

## 🏃 Running the Calibration Runner

Place your `.txt` files into `benchmarks/human/` and `benchmarks/synthetic/` directories, then run:

```bash
python benchmarks/baseline_runner.py --human benchmarks/human --synthetic benchmarks/synthetic --algorithm claude
```

---

## 📈 Sample Benchmark Output Table

```text
Benchmark Evaluation Results
════════════════════════════════════════════════════════════
Dataset             Samples    TPR (%)    FPR (%)    F1-Score
────────────────────────────────────────────────────────────
Human Baseline      1,000      --         0.8%       --
Synthetic Baseline  1,000      --         1.2%       --
Watermarked Set     1,000      93.4%      --         0.96
────────────────────────────────────────────────────────────
Calibrated Recommended Threshold: 0.65 (ClaudeMark Research Detector v0.1)
```

---

## 🔬 Scientific Honesty Notice

ClaudeMark detectors evaluate structural distributions and statistical anomalies. All threshold calibrations represent empirical benchmarks on specific evaluation sets and do not guarantee detection on unseen, heavily edited, or out-of-domain distributions.
