```
 ____ _                 _      __  __            _    
/ ___| | __ _ _   _  __| | ___|  \/  | __ _ _ __| | __
| |   | |/ _` | | | |/ _` |/ _ \ |\/| |/ _` | '__| |/ /
| |___| | (_| | |_| | (_| |  __/ |  | | (_| | |  |   < 
 \____|_|\__,_|\__,_|\__,_|\___|_|  |_|\__,_|_|  |_|\_\
```

# ClaudeMark

> **Multi-AI Watermark & Provenance Forensics Toolkit**  
> *A scientific, 100% local-first open-source research suite for statistical AI watermark analysis, Unicode steganography forensics, document cleaning, and C2PA / EXIF provenance.*

[![CI](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml/badge.svg)](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/releases)
[![Stars](https://img.shields.io/github/stars/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/stargazers)
[![Forks](https://img.shields.io/github/forks/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/forks)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Author & Maintainer:** [Karthik R Shet](https://github.com/karthikrshet)  
**Repository:** [https://github.com/karthikrshet/ClaudeMark](https://github.com/karthikrshet/ClaudeMark)  
**Latest Release:** [v1.0.0](https://github.com/karthikrshet/ClaudeMark/releases)

---

## ⚡ Quick 30-Second Demo

```bash
# 1. Clone & install
git clone https://github.com/karthikrshet/ClaudeMark.git
cd ClaudeMark

# 2. Analyze text for statistical AI signals and Unicode steganography
python claudemark.py analyze --text "In conclusion, it is important to analyze comprehensive paradigms across stakeholders."

# 3. Clean hidden metadata and zero-width markers from a document
python claudemark.py clean document.pdf -o clean.pdf

# 4. Start the interactive Web Dashboard & REST API
python claudemark.py serve --port 8765
# Open in browser: http://127.0.0.1:8765
```

---

## 🌟 Key Features

| Category | Capabilities |
| :--- | :--- |
| **🕵️ Text Forensics** | Zero-width characters (ZWSP, ZWNJ, ZWJ, BOM, Word Joiners, Unicode tags), BiDi overrides, exotic whitespace (NBSP, thin/hair space), and Latin-confusable homoglyphs. |
| **📊 Pluggable Detectors** | **Claude Research Detector** (structural burstiness & transition regularity), **Kirchenbauer Detector** (red/green list token bias), **SynthID-style Research Adapter** (entropy modulation), and **Generic Baseline**. |
| **📁 File Provenance (10 Formats)** | **Documents**: PDF, DOCX, ODT, HTML, Markdown, TXT.<br>**Images**: PNG, JPEG, WebP, SVG, AVIF, HEIC.<br>C2PA manifest verification, EXIF, XMP, IPTC, and AI-generator footprint stripping. |
| **⚡ Batch Processing** | Recursive directory tree inspection and sanitization (`claudemark inspect <dir>`, `claudemark clean <dir>`). |
| **⚖️ Forensic Diff** | Character-level deltas, anomaly reduction tracking, similarity ratios, and statistical delta shifts. |
| **💻 Web Dashboard & API** | Built-in glassmorphic dark-mode web app and OpenAPI 3.0.3 REST API. |
| **🔒 100% Local & Private** | Strictly offline execution with **zero external telemetry or network calls**. |

---

## 🏗️ Architecture & Detector Contract

ClaudeMark implements a clean, pluggable architecture with a standardized detector contract:

```text
                   ClaudeMark
                       │
                 DetectorRegistry
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
 Claude Research  Kirchenbauer   SynthID-style
    Detector        Detector     Research Adapter
        │              │              │
        └──────────────┼──────────────┘
                       ↓
                DetectionResult
        (Score, Confidence, Hypothesis, Limitations)
                       ↓
             ┌─────────┼─────────┐
             ↓         ↓         ↓
            CLI       API     Web UI
```

### Standardized Detector Contract
Every detector inherits from `WatermarkDetector` in `claudemark/detectors/base.py`:
- `detector.detect(text) -> DetectionResult` (and `analyze(text)`)
- `detector.score(text) -> float` (0.0 to 1.0)
- `detector.explain(text) -> str` (human-readable interpretation)
- `detector.limitations() -> list[str]` (documented scientific constraints)

---

## 🔬 Scientific Terminology & Methodology

To maintain strict scientific honesty and transparency:

- **Claude Research Detector**: Evaluates empirical multi-signal metrics including sentence-length burstiness variance, token transition regularity, and vocabulary compression (Yule's characteristic $K$) against natural language baselines. *Returns probabilistic research hypotheses; not definitive proof of Claude or AI authorship.*
- **Kirchenbauer Detector**: Statistical implementation based on the published Kirchenbauer et al. (2023) red/green list watermarking methodology, calculating binomial z-scores and one-tailed p-values.
- **SynthID-style Research Adapter**: Experimental research adapter modeling token probability modulation and entropy perturbation based on publicly documented principles. *Not an official Google SynthID detector.*
- **Generic Entropy Detector**: Baseline Shannon entropy and sentence length variance model.

---

## 📈 Empirical Benchmarks

ClaudeMark includes automated evaluation tooling (`benchmarks/baseline_runner.py`) for reproducible calibration across balanced corpora:

```text
Benchmark Calibration Evaluation
════════════════════════════════════════════════════════════
Dataset Category    Samples    TPR (%)    FPR (%)    F1-Score
────────────────────────────────────────────────────────────
Human Baseline      1,000      --         0.8%       --
Synthetic Baseline  1,000      --         1.2%       --
Watermarked Set     1,000      93.4%      --         0.96
────────────────────────────────────────────────────────────
Calibrated Recommended Threshold: 0.65 (ClaudeMark Research Detector v1.0)
```

---

## 🔒 Zero Network Egress Guarantee

ClaudeMark is built from the ground up for strict privacy:
- **Zero Outbound Sockets**: Core analysis, normalization, and file cleaning perform zero network transmissions.
- **Audited in CI**: Tested with blocked outbound sockets to ensure complete offline operation.
- **Air-Gap Compatible**: Can be run in fully isolated air-gapped environments.

---

## 🛠️ CLI Quick Reference

```bash
# Analyze text
python claudemark.py analyze document.txt
python claudemark.py analyze --text "Sample text..." --algorithm claude --json

# Inspect single file or entire directory
python claudemark.py inspect photo.png
python claudemark.py inspect document.pdf --json
python claudemark.py inspect ./my_documents/               # Batch directory scan

# Clean metadata and invisible watermarks
python claudemark.py clean document.pdf -o clean.pdf
python claudemark.py clean ./my_documents/ -o ./cleaned/   # Batch clean

# Safely normalize invisible Unicode markers
python claudemark.py normalize document.txt -o clean.txt

# Forensic comparison
python claudemark.py diff original.md cleaned.md

# Inspect capabilities & system tools
python claudemark.py capabilities

# Start Web UI & REST API server
python claudemark.py serve --port 8765
```

---

## 🌐 Local REST API

| Method | Endpoint | Payload / Format | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Web UI | Interactive Web Dashboard |
| `GET` | `/health` | JSON | Service health status |
| `GET` | `/capabilities` | JSON | Active detectors and supported formats |
| `GET` | `/openapi.json` | JSON | OpenAPI 3.0.3 specification |
| `POST` | `/inspect` | Base64 JSON | File inspection envelope |
| `POST` | `/clean` | Base64 JSON | File cleaning envelope |
| `POST` | `/api/analyze` | Raw JSON | Text analysis & hypothesis testing |
| `POST` | `/api/normalize` | Raw JSON | Text normalization |
| `POST` | `/api/diff` | Raw JSON | Forensic comparison |

---

## 🐳 Docker Deployment

```bash
# Build container image
docker build -t ghcr.io/karthikrshet/claudemark:latest .

# Run Web Dashboard & REST API
docker run --rm -p 8765:8765 ghcr.io/karthikrshet/claudemark:latest

# Run CLI inside container
docker run --rm -v "$(pwd):/data" ghcr.io/karthikrshet/claudemark:latest inspect /data/document.pdf
```

---

## 🧪 Testing

```bash
python -m pytest tests/
```

---

## 📜 Ethical Guidelines & Limitations

1. **Research Utility**: This toolkit is designed for researchers, authors, and developers analyzing text statistics and managing metadata on content they own or are authorized to inspect.
2. **Probabilistic Nature**: Statistical properties can vary across genres, domains, and human authors. Results represent statistical hypotheses and must not be used as conclusive evidence of authorship.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

Copyright (c) 2026 [Karthik R Shet](https://github.com/karthikrshet).
