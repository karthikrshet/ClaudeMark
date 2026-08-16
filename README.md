<div align="center">

```text
 ╔══════════════════════════════════════════════════════════════════════╗
 ║   ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗                   ║
 ║  ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝                   ║
 ║  ██║     ██║     ███████║██║   ██║██║  ██║█████╗                     ║
 ║  ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝                     ║
 ║  ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗                   ║
 ║   ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝                   ║
 ║  ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗                                 ║
 ║  ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝   [ FORENSICS LAB ]             ║
 ║  ██╔████╔██║███████║██████╔╝█████═╝    [ PROVENANCE PURIFIER ]       ║
 ║  ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗    [ ZERO-EGRESS HARDENED ]      ║
 ║  ██║ ╚═╝ ██║██║  ██║██║  ██║██║ ╚██╗                                 ║
 ║  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝                                 ║
 ║ ════════════════════════════════════════════════════════════════════ ║
 ║     LOCAL-FIRST AI WATERMARK & CONTAINER PROVENANCE PLATFORM         ║
 ╚══════════════════════════════════════════════════════════════════════╝
```

# ClaudeMark

**Scientific AI Watermark Forensics, Unicode Steganography Visualizer & Container Provenance Purifier**

[![CI](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml/badge.svg)](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/releases)
[![Stars](https://img.shields.io/github/stars/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/stargazers)
[![Forks](https://img.shields.io/github/forks/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/forks)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: 100% Offline](https://img.shields.io/badge/Network-Zero--Egress-success.svg)](SECURITY.md)

</div>

ClaudeMark is a local-first, zero-egress forensics platform engineered to detect, visualize, disrupt, and sanitize AI watermarks, steganographic carriers, and container provenance from files and text you own.

It unifies statistical text forensics and Unicode steganography visualization with defensive security auditing (decompression bomb defense, malicious PDF actions, macro detection) and atomic file sanitization.

---

## Architectural Blueprint

```text
+-----------------------------------------------------------------------------------------+
|                                     ClaudeMark Core                                     |
|  [analyze]  [unicode]  [rewrite]  [evaluate]  [inspect]  [clean]  [security]  [agent]   |
+-----------------------------------------------------------------------------------------+
       |                   |                   |                   |               |
       v                   v                   v                   v               v
+---------------+  +---------------+  +---------------+  +------------------+  +----------+
| Layer A: Core |  | Layer B: Text |  | Container Ops |  | Security Scanner |  | AI Agent |
| Unicode Scan  |  | Statistical   |  | Metadata &    |  | Decompression    |  | Tool     |
| Marker Visual |  | Detectors &   |  | C2PA JUMBF    |  | Bomb & Macro     |  | JSON-RPC |
| Normalization |  | Rewrite Lab   |  | Sanitizers    |  | Action Auditing  |  | Dispatch |
+---------------+  +---------------+  +---------------+  +------------------+  +----------+
       |                   |                   |                   |               |
       +-------------------+-------------------+-------------------+---------------+
                                           |
                                           v
                     +-------------------------------------------+
                     | Local Engine (Zero Network Egress)        |
                     | - Python 3.10+ Stdlib / Offline CPU       |
                     | - Atomic File Writes (safe_atomic_write)  |
                     | - Optional HTTP Bearer Auth Server        |
                     +-------------------------------------------+
```

---

## Complete Capability Matrix

| Forensic Dimension | Scope & Formats | Detection / Sanitization Mechanism | Verification Standard |
| :--- | :--- | :--- | :--- |
| **Unicode Steganography** | ZWSP, ZWNJ, ZWJ, WJ, BOM, MVS, Tags, VS-1..256, BiDi overrides, homoglyphs | Linear-time token scanning, visual tag formatting (`<ZWSP>`, `<BOM>`, `<RLO>`), NFC normalization | Deterministic 100% detection |
| **Statistical Watermarking** | Token selection biases, transition regularity, Shannon entropy, Kirchenbauer z-scores | Multi-detector suite (Claude research heuristic, Kirchenbauer, SynthID-style, Generic) | Probabilistic research heuristic |
| **Rewrite & Disruption** | High-frequency token rotations, sentence cadence rebalancing | Rule-based lexical restructuring, synonym rotation, before/after comparative scoring | Non-destructive local rewrite |
| **Container Provenance** | PDF, DOCX, ODT, HTML, Markdown, TXT | Document XML stream scrubbing, frontmatter key stripping, structural object rebuilding (`qpdf`) | Atomic file replacement |
| **Image Metadata** | PNG, JPEG, WebP, SVG, AVIF, HEIC | Chunk-level stripping (`tEXt`, `zTXt`, `iTXt`, `APP1`, `APP13`, RIFF `C2PA`/`XMP`) | Lossless pixel preservation |
| **Defensive Security** | Zip archives, PDF streams, Office macros | Ratio caps (100x), byte ceilings (100 MB), `/JavaScript` and `/Launch` inspection | Sandboxed execution |
| **Pixel Domain Research** | SynthID-Image, CtrlRegen, MarkDiffusion, Tree-Ring, Stable Signature | Standardized adapter interfaces for latent/spatial diffusion models | Transparent availability |
| **AI Agent Interface** | Tool execution for Claude, OpenAI, Cursor, Grok | Standardized JSON schema declarations, zero-egress local dispatcher | Loopback isolated |

---

## Demonstrations and Practical Usage

### Demo 1: Statistical AI Text Analysis

Analyze text across multiple statistical detectors to measure lexical entropy, sentence burstiness, and green-list token distributions.

```bash
python claudemark.py analyze "In conclusion, utilizing comprehensive strategic paradigms is essential for optimal operational execution." --algorithm claude --verbose
```

Output:
```json
{
  "tool": "ClaudeMark",
  "version": "2.0.0",
  "text_statistics": {
    "word_count": 13,
    "unique_words": 13,
    "sentence_count": 1,
    "type_token_ratio": 1.0,
    "shannon_entropy": 3.7004,
    "burstiness": 0.0
  },
  "watermark_result": {
    "algorithm_name": "ClaudeMark Claude Research Detector",
    "signal_score": 0.725,
    "status": "potential_signal",
    "interpretation": "Elevated transition regularity and low sentence length variance detected."
  }
}
```

---

### Demo 2: Unicode Steganography Visualizer

Invisible characters (zero-width spaces, joiners, directional overrides) are used to embed invisible payloads into text. ClaudeMark exposes them as human-readable tags.

```bash
# Text containing hidden zero-width space and right-to-left override
python claudemark.py unicode visualize "Confidential\u200bData\u202EOverride"
```

Output:
```text
Confidential<ZWSP>Data<RLO>Override
```

```bash
# Clean invisible characters and normalize Unicode
python claudemark.py unicode clean dirty.txt -o clean.txt
```

---

### Demo 3: Statistical Disruption & Rewrite Lab

Statistical watermarks exist in word transitions. The Rewrite Lab applies local syntactic transformations and synonym rotation, then calculates comparative metrics.

```bash
# Apply disruption rewrite
python claudemark.py rewrite draft.txt -o rewritten.txt --strategy synonym_cadence

# Evaluate score shift and semantic similarity
python claudemark.py evaluate draft.txt rewritten.txt
```

Output:
```text
======================================================================
 ClaudeMark Disruption Evaluation Report
======================================================================
Original Watermark Score:  0.8400
Rewritten Watermark Score: 0.3100
Watermark Delta:           -0.5300 (-63.1%)
Semantic Similarity:       0.8920 (89.2% preserved)
Character Change Ratio:    14.2%
Word Change Ratio:         18.5%
Entropy Shift:             +0.2104 bits
======================================================================
```

---

### Demo 4: Container Provenance Sanitization (10 Formats)

Strip C2PA Content Credentials, EXIF, XMP, IPTC, and AI generator metadata from documents and images using atomic replacement.

```bash
# Inspect document provenance
python claudemark.py inspect document.pdf

# Clean metadata with atomic file replacement
python claudemark.py clean document.pdf -o sanitized.pdf
python claudemark.py clean photo.png -o sanitized.png
python claudemark.py clean report.docx -o sanitized.docx
```

---

### Demo 5: C2PA Provenance Tree Extraction

Extract the hierarchical chain of claims, digital signatures, software agents, and assertions embedded inside C2PA JUMBF containers.

```bash
python claudemark.py c2pa inspect sample_with_c2pa.jpg
```

Output:
```text
C2PA Provenance Tree: sample_with_c2pa.jpg
+-- Claim Generator: Adobe Photoshop 2024 (c2pa 0.28.0)
    +-- Action: c2pa.created
    +-- Software Agent: DALL-E 3 Image Generation API
    +-- Assertion: c2pa.thumbnail (JPEG, 128x128)
    +-- Signature: Valid (Self-signed Trust Root)
```

---

### Demo 6: Defensive Security Scanner

Before processing untrusted files, scan for decompression zip bombs, malicious PDF actions, executable macros, and path traversal attempts.

```bash
python claudemark.py security scan suspicious_upload.pdf
```

Output:
```text
======================================================================
 ClaudeMark Defensive Security Report
======================================================================
File:          suspicious_upload.pdf
Threat Level:  CRITICAL
Is Safe:       False
Findings:
  [!] Malicious PDF action '/JavaScript' detected in object stream 14
  [!] Embedded executable action '/Launch' detected in trailer
======================================================================
```

---

### Demo 7: AI Agent Tool Dispatcher (Local JSON-RPC)

ClaudeMark implements a standardized tool execution interface for Claude Desktop, Cursor, OpenAI Assistants, and custom autonomous agents.

```bash
# List available agent tool schemas
python claudemark.py agent list

# Execute agent tool locally
python claudemark.py agent exec analyze_watermark --args '{"text":"Sample text to analyze", "algorithm":"claude"}'
```

---

### Demo 8: Local Web Dashboard & REST API

Launch the local standard-library web service serving both the glassmorphic dashboard and OpenAPI 3.0.3 endpoints.

```bash
python claudemark.py serve --host 127.0.0.1 --port 8765
```

- **Dashboard UI**: [http://127.0.0.1:8765/](http://127.0.0.1:8765/)
- **Health Endpoint**: [http://127.0.0.1:8765/health](http://127.0.0.1:8765/health)
- **OpenAPI 3.0.3**: [http://127.0.0.1:8765/openapi.json](http://127.0.0.1:8765/openapi.json)

---

## Supported File Formats & Sanitization Actions

| Format | Inspection Method | Sanitization Action Performed |
| :--- | :--- | :--- |
| **PDF** | Byte scan for `/Metadata`, `/Info`, and C2PA markers | Rebuilds structural object graphs (via `qpdf --linearize` or internal parser) |
| **DOCX / ODT** | Zip entry parser for `docProps/`, `meta.xml`, `customXml/` | Scrubs metadata streams and cleans body XML Unicode |
| **HTML / Markdown** | Regex parser for AI meta tags, JSON-LD, frontmatter | Drops AI attributes and cleans body text Unicode |
| **TXT** | Linear token stream scanner | Normalizes Unicode to NFC and strips zero-width/control characters |
| **PNG** | Chunk scanner for `tEXt`, `zTXt`, `iTXt`, `eXIf`, `c2pa` | Strips metadata chunks while preserving image IDAT streams |
| **JPEG** | Segment parser for `APP1` (EXIF/XMP), `APP13` (IPTC), `COM` | Drops metadata markers and retains compressed scan data |
| **WebP** | RIFF chunk parser for `EXIF`, `XMP `, `C2PA`, `ICCP` | Rebuilds RIFF container without metadata chunks |
| **SVG** | XML parser for `<metadata>`, XML comments, RDF blocks | Strips metadata elements while retaining vector geometry |

---

## Defensive Security Architecture & Hardening

All operations adhere to strict defensive engineering controls:

1. **Atomic File Writes**: Output operations write to temporary files in the target directory before performing an atomic replace (`os.replace`). If an operation is aborted mid-stream, the original file is never left in a corrupted state.
2. **Symlink Attack Defense**: Target paths are normalized and resolved; pre-existing symlinks targeting arbitrary system files are unlinked before write.
3. **Decompression Bomb Protection**: Zip containers enforce strict decompression ratio ceilings (100x) and total byte caps (100 MB).
4. **PDF Action Auditing**: Scans PDF object tables for `/JavaScript`, `/JS`, `/Launch`, `/EmbeddedFiles`, and `/SubmitForm` vectors.
5. **Macro Detection**: Flags Microsoft Office macro containers (`vbaProject.bin`).
6. **API Key Authentication**: Optional `CLAUDEMARK_SERVER_API_KEY` bearer authentication protects public endpoints.
7. **Zero Network Egress**: Zero external telemetry, tracking, or network calls during analysis.

---

## Environment Configuration

| Variable | Target | Purpose | Default |
| :--- | :--- | :--- | :--- |
| `CLAUDEMARK_PORT` | HTTP Server | Port to bind server | `8765` |
| `CLAUDEMARK_HOST` | HTTP Server | Interface to bind | `127.0.0.1` |
| `CLAUDEMARK_SERVER_API_KEY` | HTTP Server | Enforce `Authorization: Bearer <key>` | None (Open) |
| `CLAUDEMARK_MAX_INPUT_BYTES` | File Engine | Maximum allowed file size | `104857600` (100 MB) |
| `CLAUDEMARK_REWRITE_SEED` | Rewrite Engine | Deterministic seed for reproducible synonym rotation | `None` |

---

## Verification & Automated Tests

Run the complete 82-test suite covering core mathematics, detectors, format cleaners, atomic writes, bearer auth, and zero network egress:

```bash
python -m pytest tests/ -v
```

```text
============================== 82 passed in 5.88s =============================
```

---

## Ethics and Responsible Research

ClaudeMark is intended for privacy, hygiene, and forensic research on content **you own or have authorization to process**.

1. **Probabilistic Nature**: Statistical detection is based on mathematical regularities and does not constitute definitive proof of AI generation.
2. **Disruption vs. Erasure**: Disruption rewriting is experimental and does not guarantee complete signal removal.
3. **No Vendor Secrets**: Algorithms are derived from open, peer-reviewed scientific literature.

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
