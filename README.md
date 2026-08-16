```text
   ____ _                 _      __  __            _    
  / ___| | __ _ _   _  __| | ___|  \/  | __ _ _ __| | __
 | |   | |/ _` | | | |/ _` |/ _ \ |\/| |/ _` | '__| |/ /
 | |___| | (_| | |_| | (_| |  __/ |  | | (_| | |  |   < 
  \____|_|\__,_|\__,_|\__,_|\___|_|  |_|\__,_|_|  |_|\_\
  ======================================================
  AI WATERMARK FORENSICS & PROVENANCE SANITIZATION SUITE
```

# ClaudeMark

[![CI](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml/badge.svg)](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/releases)
[![Stars](https://img.shields.io/github/stars/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/stargazers)
[![Forks](https://img.shields.io/github/forks/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/forks)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

ClaudeMark is a local-first, zero-egress forensics platform designed to detect, visualize, disrupt, and sanitize AI watermarks, steganographic carriers, and container provenance from files and text you own.

It pairs scientific statistical text heuristics and Unicode marker visualization with defensive container security scanning (decompression bomb and exploit mitigation) and atomic file sanitization.

---

## Architecture Overview

```text
+-------------------------------------------------------------------------------+
|                                 ClaudeMark CLI                                |
|  [analyze]  [unicode]  [rewrite]  [evaluate]  [inspect]  [clean]  [security]  |
+-------------------------------------------------------------------------------+
       |                   |                   |                   |
       v                   v                   v                   v
+---------------+  +---------------+  +---------------+  +---------------------+
| Layer A: Core |  | Layer B: Text |  | Container Ops |  | Defensive Security  |
| Unicode Scan  |  | Statistical   |  | Metadata &    |  | Decompression Bomb  |
| Marker Visual |  | Detectors &   |  | C2PA JUMBF    |  | Macro & PDF Action  |
| Normalization |  | Rewrite Lab   |  | Sanitizers    |  | Path Traversal Guard|
+---------------+  +---------------+  +---------------+  +---------------------+
       |                   |                   |                   |
       +-------------------+-------------------+-------------------+
                                   |
                                   v
             +-------------------------------------------+
             | Local Engine (Zero Network Egress)        |
             | - Python 3.10+ Stdlib / Offline CPU       |
             | - Atomic File Writes (os.replace sandbox) |
             | - Optional HTTP Bearer Auth Server        |
             +-------------------------------------------+
```

---

## Capability Matrix

| Forensic Dimension | Scope & Target Formats | Engine / Mechanism | Security Guarantee |
| :--- | :--- | :--- | :--- |
| **Unicode Steganography** | ZWSP, ZWNJ, ZWJ, WJ, BOM, MVS, Tags, VS-1..256, BiDi overrides, homoglyphs | Linear-time token scanning, visual tag generation (`<ZWSP>`, `<BOM>`, `<RLO>`), NFC normalization | Deterministic 100% detection |
| **Statistical Watermarking** | Token selection biases, transition regularity, Shannon entropy, Kirchenbauer z-scores | Multi-detector suite (Claude research heuristic, Kirchenbauer, SynthID-style, Generic) | Probabilistic research heuristic |
| **Rewrite & Disruption** | High-frequency token rotations, sentence cadence rebalancing | Rule-based lexical restructuring, synonym rotation, before/after comparative scoring | Non-destructive local rewrite |
| **Container Provenance** | PDF, DOCX, ODT, HTML, Markdown, TXT | Document XML stream scrubbing, frontmatter key stripping, object linearization (`qpdf`) | Atomic file replacement |
| **Image Metadata** | PNG, JPEG, WebP, SVG, AVIF, HEIC | Chunk-level stripping (`tEXt`, `zTXt`, `iTXt`, `APP1`, `APP13`, RIFF `C2PA`/`XMP`) | Lossless pixel preservation |
| **Defensive Security** | Zip archives, PDF streams, Office macros | Ratio caps (100x), byte ceilings (100 MB), `/JavaScript` and `/Launch` inspection | Sandboxed execution |
| **AI Agent Interface** | Tool execution for Claude, OpenAI, Cursor, Grok | Standardized JSON schema declarations, zero-egress local dispatcher | Loopback isolated |

---

## Quickstart

### 1. Environment Setup

```bash
# Automated setup (Linux / macOS)
bash setup_env.sh

# Automated setup (Windows PowerShell)
powershell -ExecutionPolicy Bypass -File setup_env.ps1

# Or manual installation
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

### 2. Command Line Operations

```bash
# Text analysis across statistical detectors
python claudemark.py analyze sample.txt --algorithm claude --verbose
python claudemark.py analyze sample.txt --algorithm kirchenbauer --json

# Unicode forensics: inspect, visualize hidden marks, clean
python claudemark.py unicode inspect draft.txt
python claudemark.py unicode visualize draft.txt      # Outputs: Hello<ZWSP>world<RLO>
python claudemark.py unicode clean draft.txt -o clean.txt

# Statistical watermark disruption & comparative evaluation
python claudemark.py rewrite draft.txt -o rewritten.txt --strategy synonym_cadence
python claudemark.py evaluate draft.txt rewritten.txt

# Container inspection & atomic sanitization
python claudemark.py inspect document.pdf
python claudemark.py clean document.pdf -o sanitized.pdf
python claudemark.py inspect photo.png
python claudemark.py clean photo.png -o sanitized.png

# C2PA provenance hierarchy extraction
python claudemark.py c2pa inspect sample.jpg

# Defensive container security scan
python claudemark.py security scan incoming_archive.zip

# Start local web dashboard & REST API
python claudemark.py serve --host 127.0.0.1 --port 8765
```

---

## Text Tools Binary Guard

Text commands (`analyze`, `unicode`, `rewrite`) automatically inspect header magic bytes and control character distributions. If a user inadvertently points a text command at a binary container (`.docx`, `.pdf`, `.png`), ClaudeMark rejects the execution to protect the underlying file structure:

```bash
python claudemark.py unicode inspect document.docx
# Refusing binary input: file contains ZIP container signature. Use 'inspect' or 'clean' instead.
```

---

## HTTP REST API & Web Dashboard

ClaudeMark provides a self-contained standard library server (`claudemark/server.py`) serving both an interactive dark-mode dashboard and a machine-readable REST API:

| Method | Endpoint | Request Body | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | None | Service health status and version |
| `GET` | `/capabilities` | None | List active detectors, supported formats, and system tools |
| `GET` | `/openapi.json` | None | Dynamically generated OpenAPI 3.0.3 contract |
| `POST` | `/inspect` | `{"file": "<base64>", "name": "doc.pdf"}` | Base64 file inspection returning provenance findings |
| `POST` | `/clean` | `{"file": "<base64>", "name": "doc.pdf"}` | Base64 file cleaning returning sanitized payload |
| `POST` | `/api/analyze` | `{"text": "...", "algorithm": "claude"}` | Statistical watermark and metric evaluation |
| `POST` | `/api/unicode/analyze` | `{"text": "..."}` | Deep Unicode anomaly inspection |
| `POST` | `/api/unicode/visualize`| `{"text": "..."}` | Visual tag conversion for invisible characters |
| `POST` | `/api/rewrite` | `{"text": "...", "strategy": "synonym_cadence"}` | Best-effort statistical watermark disruption |
| `POST` | `/api/evaluate` | `{"original": "...", "processed": "..."}` | Comparative metrics and score shift analysis |
| `POST` | `/api/security/scan` | `{"file": "<base64>", "name": "file.zip"}` | Decompression bomb and macro exploit scan |
| `POST` | `/api/agent/exec` | `{"tool_name": "...", "arguments": {...}}` | AI Agent local tool dispatch |

---

## Security Architecture & Hardening

ClaudeMark implements defensive engineering principles across all file operations:

1. **Atomic File Writes**: Output operations write to temporary files in the target directory before performing an atomic replace (`os.replace`). If an execution is terminated mid-stream, original files remain undamaged.
2. **Symlink Attack Defense**: Target paths are resolved and unlinked if an adversarial symlink is pre-placed.
3. **Decompression Bomb Protection**: Zip containers enforce strict decompression ratio ceilings (100x) and total byte caps (100 MB).
4. **PDF Action Auditing**: Scans PDF object tables for `/JavaScript`, `/JS`, `/Launch`, `/EmbeddedFiles`, and `/SubmitForm` vectors.
5. **Macro Detection**: Flags Microsoft Office macro containers (`vbaProject.bin`).
6. **API Key Authentication**: Optional `CLAUDEMARK_SERVER_API_KEY` bearer authentication protects public endpoints.
7. **Zero Network Egress**: Zero external telemetry, tracking, or network requests during analysis.

---

## Research Framework & Pixel Domain Adapters

For academic research, ClaudeMark provides standardized adapter interfaces in `claudemark/pixel/`:

- **SynthID-Image Adapter**: Frequency-domain and spectral codebook research interface.
- **CtrlRegen Adapter**: Controllable regeneration research interface.
- **MarkDiffusion Adapter**: Generative diffusion watermark harness and blind purification.
- **Tree-Ring / Ring-ID Adapter**: Circular frequency-domain watermark detection interface.
- **Stable Signature Adapter**: Latent extractor evaluation interface.
- **StegaStamp Adapter**: Deep steganographic decoder interface.

When heavy ML checkpoints are not installed locally, adapters report `available: false` with explicit installation instructions, avoiding silent failures.

---

## Verification & Test Suite

Run the complete 82-test suite covering core mathematics, detectors, format cleaners, atomic writes, bearer auth, and zero network egress:

```bash
python -m pytest tests/ -v
```

```text
============================== 82 passed in 5.88s =============================
```

---

## License

ClaudeMark is licensed under the [MIT License](LICENSE).  
Author: [Karthik R Shet](https://github.com/karthikrshet)

---

## Scientific References

- Meyer, G., *watermarks-remover: Agent skill + stdlib Python service to strip multi-vendor AI provenance marks* (https://github.com/guillaumemeyer/watermarks-remover).
- Dathathri et al., *Scalable watermarking for identifying large language model outputs* (Nature 2024, SynthID-Text).
- Kirchenbauer et al., *A Watermark for Large Language Models* (ICML 2023).
- Content Authenticity Initiative, *C2PA Technical Specification* (c2pa.org).
- Liu et al., *Image Watermarks are Removable Using Controllable Regeneration from Clean Noise* (ICLR 2025, CtrlRegen).
- Pan et al., *MarkDiffusion: An Open-Source Toolkit for Generative Watermarking of Latent Diffusion Models* (JMLR 2025).
- Zhang et al., *Watermarks in the Sand: Impossibility of Strong Watermarking for Generative Models* (ICML 2024).
- Kassis & Hengartner, *UnMarker: A Universal Attack on Defensive Image Watermarking* (IEEE S&P 2025).
- Goonatilake & Ateniese, *Removing the Watermark Is Not Enough: Forensic Stealth in Generative-AI Watermark Removal* (arXiv:2605.09203).
