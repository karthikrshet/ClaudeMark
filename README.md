```
 ____ _                 _      __  __            _    
/ ___| | __ _ _   _  __| | ___|  \/  | __ _ _ __| | __
| |   | |/ _` | | | |/ _` |/ _ \ |\/| |/ _` | '__| |/ /
| |___| | (_| | |_| | (_| |  __/ |  | | (_| | |  |   < 
 \____|_|\__,_|\__,_|\__,_|\___|_|  |_|\__,_|_|  |_|\_\
```

# ClaudeMark v2

> **Complete AI Watermark, Provenance Forensics & Disruption Platform**  
> *A scientific, 100% local-first open-source research suite for multi-AI watermark detection, Unicode steganography forensics, document sanitization, C2PA / EXIF provenance trees, statistical disruption rewriting, and defensive container security.*

[![CI](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml/badge.svg)](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/releases)
[![Stars](https://img.shields.io/github/stars/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/stargazers)
[![Forks](https://img.shields.io/github/forks/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/forks)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Author & Maintainer:** [Karthik R Shet](https://github.com/karthikrshet)  
**Repository:** [https://github.com/karthikrshet/ClaudeMark](https://github.com/karthikrshet/ClaudeMark)  
**Latest Release:** [v2.0.0](https://github.com/karthikrshet/ClaudeMark/releases)

---

## ⚡ Quick 30-Second Demo

```bash
# 1. Clone & install
git clone https://github.com/karthikrshet/ClaudeMark.git
cd ClaudeMark

# 2. Analyze text for statistical AI signals and Unicode steganography
python claudemark.py analyze --text "In conclusion, it is important to analyze comprehensive paradigms across stakeholders."

# 3. Reveal invisible Unicode watermarks visually
python claudemark.py unicode visualize input.txt

# 4. Best-effort statistical watermark disruption & rewriting
python claudemark.py rewrite input.txt -o rewritten.txt

# 5. Evaluate before/after watermark score shifts and semantic similarity
python claudemark.py evaluate input.txt rewritten.txt

# 6. Defensively scan files for zip bombs, macros, and malicious PDF actions
python claudemark.py security scan document.pdf

# 7. Start the interactive Web Dashboard & REST API
python claudemark.py serve --port 8765
# Open in browser: http://127.0.0.1:8765
```

---

## 🌟 Capabilities Matrix

| Capability Category | ClaudeMark v2 | Description |
| :--- | :---: | :--- |
| **🕵️ Unicode / Invisible Forensics** | ⭐⭐⭐⭐⭐ | Detects ZWSP, ZWNJ, ZWJ, WJ, BOM, TAGs, Variation Selectors, BiDi overrides, NBSP, and homoglyphs. Provides `inspect`, `visualize` (`Hello<ZWSP>world`), `normalize`, `clean`, and `diff`. |
| **📊 Statistical AI Detectors** | ⭐⭐⭐⭐⭐ | Pluggable engines: Claude Research Detector, Kirchenbauer (Green/Red token z-score), SynthID-style entropy modulation adapter, and Generic Baseline. |
| **🔄 Statistical Disruption & Rewrite** | ⭐⭐⭐⭐⭐ | Best-effort text restructuring, synonym rotation, cadence rebalancing, with before/after scoring, edit distance, and semantic similarity tracking. |
| **🖼️ Image & Pixel Forensics** | ⭐⭐⭐⭐⭐ | Container parsing for PNG, JPEG, WebP, SVG, AVIF, HEIC. Pluggable pixel research adapters for SynthID-Image, CtrlRegen, MarkDiffusion, Tree-Ring, Stable Signature, and StegaStamp. |
| **🛡️ C2PA & Provenance Trees** | ⭐⭐⭐⭐⭐ | Manifest detection, JUMBF parsing, claim extraction, software agent detection, actions, assertions, and formatted ASCII provenance trees. |
| **📁 Document Sanitization** | ⭐⭐⭐⭐⭐ | Zero-leakage metadata scrubbing across PDF, DOCX, ODT, HTML, Markdown, and TXT with zip bomb and macro safety defenses. |
| **🛡️ Defensive Security Hardening** | ⭐⭐⭐⭐⭐ | Zip bomb ratio checks, malicious PDF action scanning (`/JavaScript`, `/Launch`), macro detection (`vbaProject.bin`), Windows reserved device guards, and path traversal sanitization. |
| **🤖 AI Agent Tooling** | ⭐⭐⭐⭐⭐ | Native MCP-compatible tool schema and dispatcher (`analyze_watermark`, `analyze_unicode`, `inspect_provenance`, `clean_file`, `disrupt_watermark`, `scan_security`, `get_capabilities`). |
| **💻 Glassmorphic Web Dashboard** | ⭐⭐⭐⭐⭐ | 16 interactive tabs, visual gauges, provenance trees, Unicode visualization, rewrite lab, metadata table, and diff viewer. |
| **🔒 100% Local & Zero Egress** | ⭐⭐⭐⭐⭐ | Strictly offline execution with **zero external telemetry or network calls**. |

---

## 🏗️ Architecture & Component Hierarchy

```text
                                  ClaudeMark v2
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         ↓                              ↓                              ↓
      ANALYZE                        INSPECT                         CLEAN / REWRITE
         │                              │                              │
 ┌───────┴───────┐              ┌───────┴───────┐              ┌───────┴───────┐
 │  Statistical  │              │  C2PA / EXIF  │              │    Unicode    │
 │   Detectors   │              │   Metadata    │              │  Normalizer   │
 ├───────────────┤              ├───────────────┤              ├───────────────┤
 │ • Claude Mark │              │ • C2PA Trees  │              │ • Zero-width  │
 │ • Kirchenbauer│              │ • EXIF / XMP  │              │ • BiDi / NBSP │
 │ • SynthID-text│              │ • IPTC / Tags │              │ • Homoglyphs  │
 │ • Generic     │              │ • Document Xml│              │ • Disruption  │
 └───────────────┘              └───────────────┘              └───────────────┘
         │                              │                              │
         └──────────────────────────────┼──────────────────────────────┘
                                        ↓
                              UNIFIED FORENSIC ENGINE
                                        ↓
         ┌──────────────────────────────┼──────────────────────────────┐
         ↓                              ↓                              ↓
      CLI TOOLS                     REST API & WEB                  AI AGENTS
  claudemark analyze             http://127.0.0.1:8765         JSON Schema Tooling
  claudemark unicode             /api/unicode/analyze          Local Tool Dispatcher
  claudemark rewrite             /api/rewrite                  Zero-Egress Security
  claudemark security            /api/security/scan
```

---

## 📋 Comprehensive CLI Reference

### 1. Unicode & Steganography Forensics
```bash
# Inspect text for invisible characters and homoglyphs
claudemark unicode inspect suspicious.txt

# Visualize invisible characters with human-readable tags (<ZWSP>, <BOM>, <RLO>)
claudemark unicode visualize suspicious.txt

# Clean zero-width characters and normalize Unicode
claudemark unicode clean suspicious.txt -o clean.txt
```

### 2. Statistical Watermark Analysis
```bash
# Analyze text with the Claude Research Detector
claudemark analyze sample.txt --algorithm claude --verbose

# Run Kirchenbauer green-token statistical analysis
claudemark analyze sample.txt --algorithm kirchenbauer --json

# Compare original and edited text
claudemark diff original.txt edited.txt
```

### 3. Statistical Watermark Disruption (Rewrite Lab)
```bash
# Best-effort statistical watermark disruption via text restructuring
claudemark rewrite input.txt -o rewritten.txt --strategy synonym_cadence

# Evaluate watermark score shifts and semantic preservation
claudemark evaluate input.txt rewritten.txt
```

### 4. File Provenance & C2PA Hierarchy
```bash
# Inspect any document or image for C2PA, EXIF, and AI footprints
claudemark inspect photo.png

# Display ASCII C2PA Provenance Tree
claudemark c2pa inspect sample.jpg

# Clean metadata from documents or images
claudemark clean document.docx -o clean.docx
```

### 5. Defensive Security Scanner
```bash
# Defensively scan files for zip bombs, malicious PDF actions, and macros
claudemark security scan upload.pdf
```

### 6. AI Agent Tool Interface
```bash
# List all available agent tool schemas
claudemark agent list

# Execute an agent tool locally
claudemark agent exec analyze_unicode --args '{"text":"Hello\u200bWorld"}'
```

---

## 🧪 Benchmark Framework & Empirical Evaluation

ClaudeMark includes an empirical evaluation pipeline in `benchmarks/` measuring:
- **True Positive Rate (TPR)**
- **False Positive Rate (FPR)**
- **Precision, Recall, & F1-Score**
- **Entropy & Burstiness Calibrations**

```bash
python benchmarks/baseline_runner.py --human benchmarks/human --synthetic benchmarks/synthetic --algorithm claude
```

---

## 🔬 Scientific Honesty & Positioning

1. **Probabilistic Research Signals**: Statistical detectors measure structural token regularities, burstiness anomalies, and entropy modulation. They are research tools and do not represent definitive authorship proof.
2. **Proprietary Vendor Independence**: ClaudeMark does not claim access to proprietary internal weights or vendor secrets. All algorithms are based on peer-reviewed open scientific literature (Kirchenbauer et al., SynthID specifications, and information-theoretic distributions).
3. **Disruption vs. Erasure**: Watermark disruption via text restructuring is a best-effort research technique with no guarantee of complete signal removal.

---

## 🔒 Privacy & Zero-Egress Guarantee

- **100% Local Execution**: All detectors, normalizers, metadata cleaners, and security scanners run entirely offline on your local CPU.
- **Zero Network Telemetry**: ClaudeMark never sends your documents, text, or file data to external servers.
- **Defensive Sandboxing**: Built-in protections against zip bombs, decompression exhaustion, path traversal, and malicious PDF scripts.

---

## 📄 License

ClaudeMark is released under the **MIT License**. Created by [Karthik R Shet](https://github.com/karthikrshet).
