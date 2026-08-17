<div align="center">

<p align="center">
  <img src="assets/logo.svg" width="96" height="96" alt="ClaudeMark Logo" />
</p>

# Claude<span style="color:#06B6D4">Mark</span>

### Multi-AI Watermark & Provenance Forensics

**Deterministic Multi-AI Detection, Zero-Width Steganography Sanitization & C2PA / EXIF / XMP Provenance Purifier**

[![CI](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml/badge.svg)](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/releases)
[![Stars](https://img.shields.io/github/stars/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/stargazers)
[![Forks](https://img.shields.io/github/forks/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/forks)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: 100% Offline](https://img.shields.io/badge/Network-Zero--Egress-success.svg)](SECURITY.md)

</div>

ClaudeMark is a local-first, zero-egress forensics platform engineered to detect, visualize, disrupt, and sanitize AI watermarks, steganographic carriers, and container provenance from files and text you own.

It unifies statistical text forensics and Unicode steganography visualization with defensive security auditing (decompression bomb defense, malicious PDF actions, macro detection) and atomic file sanitization.

| Layer | Target | Mechanism |
| :--- | :--- | :--- |
| **Layer A (Deterministic)** | Invisible Unicode, ZWSP, ZWNJ, ZWJ, WJ, BOM, MVS, Unicode Tags, Variation Selectors, BiDi overrides, exotic spaces, homoglyphs | Linear-time token analysis, NFC normalization, steganography visualizer (`<ZWSP>`, `<BOM>`, `<RLO>`) |
| **Layer B (Statistical Text)** | Statistical token bias, transition regularity, entropy modulation, Kirchenbauer red/green list bias | Multi-detector suite (Claude research heuristic, Kirchenbauer, SynthID-style, Generic) + best-effort disruption rewrite |
| **Files & Containers** | C2PA manifests, JUMBF containers, EXIF, XMP, IPTC, document XML streams, generator signatures | Structural metadata stripping for PNG, JPEG, WebP, SVG, AVIF, HEIC, PDF, DOCX, ODT, HTML, Markdown |
| **Defensive Security** | Decompression bombs, malicious PDF actions, executable VBA macros, path traversal | Zip compression ratio limits (100x), action scanning (`/JavaScript`, `/Launch`), macro detection (`vbaProject.bin`) |
| **Pixel Domain (Research)** | Latent and spatial image watermarks | Standardized research adapters for SynthID-Image, CtrlRegen, MarkDiffusion, Tree-Ring, Stable Signature, StegaStamp |
| **AI Agent Interface** | Tool execution for Claude, OpenAI, Cursor, Grok | Standardized JSON schema declarations, zero-egress local dispatcher |

Vendors and ecosystems evaluated: **Claude (Anthropic research heuristics)**, **Gemini / SynthID-Text**, **OpenAI provenance surfaces**, **open-LLM Kirchenbauer-class schemes**.

---

## Why ClaudeMark?

| Pillar | Focus | Capability |
| :--- | :--- | :--- |
| **Detection** | Statistical Research Signals | Entropy, burstiness, Kirchenbauer z-scores, and Claude heuristic signals |
| **Forensics** | Unicode & Steganography | Renders invisible bytes as readable tags (`<ZWSP>`, `<BOM>`, `<RLO>`) |
| **Inspection** | C2PA & Metadata | Manifest extraction, claim generators, software agents, and provenance trees |
| **Sanitization** | Container Cleaning | Strips C2PA/EXIF/XMP from 12 document and image formats with atomic replacement |
| **Security** | Defensive File Auditing | Scans for zip bombs ($100\times$ cap), malicious PDF actions, and VBA macros |
| **Comparison** | Before/After Analysis | Quantifies score shifts, token divergence, and semantic preservation |
| **Automation** | CLI, API & AI Agents | Unified single-binary CLI, local REST service, and native agent tools |

---

## Limitations

ClaudeMark is a research and forensic analysis toolkit designed for authorized content you own.

1. **Statistical signals do not prove AI authorship**: An elevated statistical signal reflects mathematical regularities, not definitive proof of authorship by a specific model or vendor.
2. **No proprietary model access**: ClaudeMark does not claim access to proprietary model weights, private vendor watermark keys, or undocumented vendor detection APIs.
3. **Disruption is best-effort**: Statistical watermark disruption is experimental. A reduced score indicates structural alteration, not a guarantee that a watermark has been erased or that another detector will classify the text differently.
4. **Provenance presence vs. absence**: C2PA and metadata findings represent data present in the examined container; the absence of metadata does not prove that content is human-created or provenance-free.

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

---

## Universal Agent Ecosystem & Skill Integrations

ClaudeMark provides native, zero-egress agent skills, rule definitions, and schema contracts for all major AI coding environments:

| Environment | Integration Path | Features |
| :--- | :--- | :--- |
| **Antigravity IDE** | `.agents/skills/ai-forensics/` & `.agents/rules/` | Automatic IDE skill discovery, inline steganography linting |
| **Claude Desktop / Code** | `.claude/skills/ai-forensics/` & MCP tools | Tool dispatch over local stdlib server |
| **Cursor IDE** | `.cursor/rules/clean-user-facing-text.mdc` | Manuscript hygiene rule and workspace skill |
| **OpenAI Codex / ChatGPT** | `claudemark schema` & JSON-RPC | OpenAI-compatible tool calling schemas |
| **Grok** | `.grok/skills/ai-forensics/` | Project-local agent skills |

```bash
# Universal installer across all environments (Cursor, Antigravity, Claude, Grok, Codex)
python install_skill.py --target all

# Or install for a specific agent host
python install_skill.py --target antigravity
python install_skill.py --target cursor
python install_skill.py --target claude
python install_skill.py --target grok
```

---

## Quickstart & Installation

```bash
# Automated bootstrap (Linux / macOS)
bash setup_env.sh

# Automated bootstrap (Windows PowerShell)
powershell -ExecutionPolicy Bypass -File setup_env.ps1

# Manual setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

---

## Command Line Usage (CLI)

```bash
# 1. Text Analysis (Statistical watermark signal + Unicode anomalies)
python claudemark.py analyze sample.txt --algorithm claude --verbose
python claudemark.py analyze sample.txt --algorithm kirchenbauer --json

# 2. Unicode Forensics (Inspect, Visualize, Clean)
python claudemark.py unicode inspect draft.txt
python claudemark.py unicode visualize draft.txt      # Exposes <ZWSP>, <BOM>, <RLO>, etc.
python claudemark.py unicode clean draft.txt -o clean.txt

# 3. Statistical Disruption, Rewrite Lab & Interactive HTML Diff
python claudemark.py rewrite draft.txt -o rewritten.txt --strategy synonym_cadence
python claudemark.py evaluate draft.txt rewritten.txt # Measures score shift, semantic similarity, entropy delta
python claudemark.py diff draft.txt rewritten.txt --html -o diff_report.html # Side-by-side visual HTML diff

# 4. File & Multimedia Provenance Sanitization (16 formats)
python claudemark.py inspect document.pdf
python claudemark.py clean document.pdf -o clean.pdf
python claudemark.py clean photo.png -o clean_photo.png
python claudemark.py clean image.avif -o clean_image.avif
python claudemark.py clean video.mp4 -o clean_video.mp4
python claudemark.py clean audio.mp3 -o clean_audio.mp3

# 5. Concurrent Multi-Threaded Directory Tree Audit
python claudemark.py audit .                         # Fast parallel multi-threaded scan
python claudemark.py audit . --json                  # Structured findings report

# 6. JSON Schema Export (For AI Agents & Automation)
python claudemark.py schema                          # Exports JSON Schemas for tool calling & APIs

# 7. C2PA Hierarchy & Provenance Trees
python claudemark.py c2pa inspect image.jpg

# 8. Defensive Security Scanner
python claudemark.py security scan upload.pdf

# 9. AI Agent Tool Dispatcher (Local & zero-egress)
python claudemark.py agent list
python claudemark.py agent exec analyze_watermark --args '{"text":"Sample text", "algorithm":"claude"}'

# 10. Start Local Web Dashboard & REST API
python claudemark.py serve --host 127.0.0.1 --port 8765
```

---

## Text Tools Refuse Binary Input

`analyze`, `unicode`, and `rewrite` operate on text. When pointed at binary files (`.docx`, `.pdf`, `.png`), ClaudeMark verifies file signatures and control-byte distributions to reject raw binary execution, preventing file corruption:

```bash
python claudemark.py unicode inspect document.docx
# Refusing binary input: file contains ZIP container signature. Use 'inspect' or 'clean' instead.
```

---

## HTTP REST Service

ClaudeMark includes a built-in standard library HTTP service (`claudemark/server.py`) serving both the interactive glassmorphic web dashboard and a machine-readable REST API:

| Method | Path | Body / Query | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | None | Service health status and version |
| `GET` | `/capabilities` | None | Active detectors, supported document/image formats, and system tools |
| `GET` | `/openapi.json` | None | Dynamically generated OpenAPI 3.0.3 specification |
| `POST` | `/inspect` | `{"file": "<base64>", "name": "doc.pdf"}` | Base64 file inspection returning provenance findings and risk status |
| `POST` | `/clean` | `{"file": "<base64>", "name": "doc.pdf"}` | Base64 file cleaning returning sanitized payload and action report |
| `POST` | `/api/analyze` | `{"text": "...", "algorithm": "claude", "threshold": 0.65}` | Statistical watermark and text metrics analysis |
| `POST` | `/api/unicode/analyze` | `{"text": "..."}` | Detailed Unicode anomaly inspection |
| `POST` | `/api/unicode/visualize` | `{"text": "..."}` | Renders hidden Unicode markers into visible tag syntax |
| `POST` | `/api/rewrite` | `{"text": "...", "strategy": "synonym_cadence"}` | Best-effort statistical watermark disruption |
| `POST` | `/api/evaluate` | `{"original": "...", "processed": "...", "algorithm": "claude"}` | Before/after comparative metrics evaluation |
| `POST` | `/api/diff` | `{"original": "...", "processed": "..."}` | Forensic text diff with anomaly reduction tracking |
| `POST` | `/api/security/scan` | `{"file": "<base64>", "name": "file.zip"}` | Decompression bomb and macro exploit scan |
| `POST` | `/api/agent/tools` | None | Lists available agent tool definitions in JSON schema |
| `POST` | `/api/agent/exec` | `{"tool_name": "...", "arguments": {...}}` | Executes agent tool invocation locally |

```bash
# Health check
curl -s http://127.0.0.1:8765/health

# Analyze text via REST
curl -s -X POST http://127.0.0.1:8765/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "In conclusion, comprehensive strategic paradigms are essential.", "algorithm": "claude"}'
```

Set `CLAUDEMARK_SERVER_API_KEY` in your environment to enforce `Authorization: Bearer <key>` on all operational endpoints.

---

## Docker & Compose Infrastructure

ClaudeMark runs inside isolated containers with read-only root filesystems and non-root execution:

```bash
# Build and run with Docker Compose
docker compose up -d

# Check service health
curl -s http://127.0.0.1:8765/health
```

Optional external system dependencies (automatically used when present on host or in container):

| System Tool | Role |
| --- | --- |
| `c2patool` | Cryptographic verification of C2PA manifests and signatures |
| `exiftool` | Secondary metadata inspection and residual block scrubbing |
| `qpdf` | Structural PDF object rebuilding and unreferenced object linearization |

---

## CI/CD, GitHub Actions & Pre-Commit Integration

### Official GitHub Action
Integrate ClaudeMark directly into your GitHub CI/CD workflows to scan Pull Requests and prevent unstripped tracking manifests or invisible Unicode markers:

```yaml
- name: Audit Repository with ClaudeMark
  uses: karthikrshet/ClaudeMark@v2.0.0
  with:
    path: '.'
    fail-on-suspicious: 'true'
```

### Pre-Commit Hook
Prevent invisible steganography and container tracking from ever entering your Git repository by adding ClaudeMark to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/karthikrshet/ClaudeMark
    rev: v2.0.0
    hooks:
      - id: claudemark-clean-unicode
      - id: claudemark-audit
```

---

## Cryptographic Forensic Audit Certificate Export

Generate verifiable, print-ready, standalone HTML audit certificates with SHA-256 integrity digests, timestamp signatures, and risk evaluations:

```bash
# Generate standalone HTML forensic certificate for a document
python claudemark.py inspect document.pdf --certificate audit_certificate.html
```

---

## Environment Configuration

Configuration variables are supported via environment exports or a local `.env` file (gitignored by default):

| Variable | Target | Purpose | Default |
| --- | --- | --- | --- |
| `CLAUDEMARK_PORT` | HTTP Server | Port to bind server | `8765` |
| `CLAUDEMARK_HOST` | HTTP Server | Interface to bind | `127.0.0.1` |
| `CLAUDEMARK_SERVER_API_KEY` | HTTP Server | Enforce `Authorization: Bearer <key>` | None (Open) |
| `CLAUDEMARK_MAX_INPUT_BYTES` | File Engine | Maximum allowed file size | `104857600` (100 MB) |
| `CLAUDEMARK_REWRITE_SEED` | Rewrite Engine | Deterministic seed for reproducible synonym rotation | `None` |

---

## Optional Pixel-Domain Watermark Research Framework

For pixel-domain image watermarks, ClaudeMark provides standardized research adapters in `claudemark/pixel/`:

1. **SynthID-Image Adapter**: Interface for spectral codebook and frequency-domain evaluation.
2. **CtrlRegen Adapter**: Interface for ControlNet + DINOv2 controllable regeneration attacks.
3. **MarkDiffusion Adapter**: Generative latent diffusion watermark verification harness and `DiffusionPurification` blind regeneration.
4. **Tree-Ring / Ring-ID Adapter**: Frequency-domain circular watermark detection interface.
5. **Stable Signature Adapter**: Latent extractor evaluation interface.
6. **StegaStamp Adapter**: Deep steganographic decoder interface.

Heavy research checkpoints are **not bundled** into the lightweight core package. When model weights are unconfigured, adapters report:

```json
{
  "backend_name": "synthid-image",
  "available": false,
  "details": {
    "message": "SynthID-Image requires official research checkpoints."
  }
}
```

---

## Optional MarkLLM Text-Watermark Verification

For controlled scientific experiments, ClaudeMark provides integration points for [THU-BPM/MarkLLM](https://github.com/THU-BPM/MarkLLM) evaluation harnesses. This allows benchmarking:
- **KGW (Kirchenbauer et al.)** green/red list token sampling.
- **SynthID-Text** distribution modulation.
- Verification before and after Layer B disruption passes.

---

## Coverage Matrix

| Channel | Claude Research | Gemini / SynthID | OpenAI Surfaces | Open-LLM / KGW |
| --- | --- | --- | --- | --- |
| **Layer A: Unicode & Edit Marks** | Yes (Deterministic) | Yes (Deterministic) | Yes (Deterministic) | Yes (Deterministic) |
| **Layer B: Statistical Sampling** | Research Heuristic | Research Adapter | Experimental | Published z-score test |
| **C2PA / Container Metadata** | Supported formats | Supported formats | Supported formats | Supported formats |
| **Pixel Domain Watermarks** | Adapter framework | Adapter framework | Adapter framework | Adapter framework |

---

## How Text Marking Works

Modern LLM watermarks embed signals in **token selection frequencies** (generative sampling bias) or **invisible formatting carriers**:

1. **Layer A (Deterministic)**: Removes invisible Unicode carriers (zero-width spaces, joiners, tags, directional overrides, homoglyphs).
2. **Layer B (Statistical Disruption)**: Disrupts token-level sampling biases via syntax restructuring, synonym substitution, and cadence rebalancing.
3. **File Sanitizers**: Removes C2PA, EXIF, XMP, IPTC, and generator properties from document and image containers.

---

## Disclaimer on Statistical Watermark Disruption

Statistical watermarks exist in **word choices and syntactic transitions**. The signal is distributed across sentences, meaning:

1. **Disruption requires rewording, not formatting tweaks.** Superficial re-indentation or spacing changes do not alter token-choice distributions.
2. **Rewording alters writing cadence.** Best-effort rewriting replaces specific vocabulary and sentence lengths, which can impact stylistic nuance.
3. **No magic eraser exists.** Statistical detection is probabilistic. ClaudeMark provides experimental research transformations with transparent before/after metrics, not absolute evasion guarantees.

---

## File Format Capabilities

| Format | Inspection Method | Sanitization Action |
| --- | --- | --- |
| **PNG** | Chunk scanner for `tEXt`, `zTXt`, `iTXt`, `eXIf`, `c2pa` | Strips metadata chunks while preserving image IDAT streams |
| **JPEG** | Segment parser for `APP1` (EXIF/XMP), `APP13` (IPTC), `COM` | Drops metadata markers and retains compressed scan data |
| **WebP** | RIFF chunk parser for `EXIF`, `XMP `, `C2PA`, `ICCP` | Rebuilds RIFF container without metadata chunks |
| **AVIF / HEIC** | ISOBMFF box parser for `ftyp`, `meta`, `iloc`, `mdat` | Reconstructs container and strips `c2pa`, `Exif`, `xml ` boxes |
| **MP4 / MOV / M4A** | ISOBMFF multimedia box parser for `ftyp`, `moov`, `mdat` | Drops `udta`, `c2pa`, `uuid`, and `XMP_` metadata atoms |
| **MP3** | ID3v2 and ID3v1 tag byte frame analyzer | Strips ID3v2 header and ID3v1 trailer tags from audio streams |
| **SVG** | XML parser for `<metadata>`, XML comments, RDF blocks | Strips metadata elements while retaining vector geometry |
| **PDF** | Byte scan for `/Metadata`, `/Info`, and C2PA markers | Rebuilds structural object graphs (via `qpdf` or internal sanitizer) |
| **DOCX / ODT** | Zip entry parser for `docProps/`, `meta.xml`, `customXml/` | Scrubs metadata streams and cleans body XML Unicode |
| **HTML / Markdown** | Regex and tag parser for AI meta tags, JSON-LD, frontmatter | Drops AI attributes and cleans body text Unicode |

#### Why PDF Requires Structural Rebuilding

Standard metadata tools often append update records to PDFs rather than rewriting object tables. ClaudeMark integrates with `qpdf --linearize` when available to rewrite the object graph, ensuring unreferenced metadata streams are removed.

---

## Residual Risk After a Clean

| Channel | What ClaudeMark Sanitizes | What May Remain | External Verification Reference |
| --- | --- | --- | --- |
| **Hard-bound C2PA / EXIF / XMP** | Yes (stripped from container) | In-content soft bindings | [c2patool](https://github.com/contentauth/c2pa-rs), [Content Credentials](https://contentcredentials.org/verify) |
| **Invisible Steganography** | Yes (all zero-width and control chars) | Normal visible text | Built-in `unicode inspect` and `visualize` |
| **Statistical Token Marks** | Best-effort disruption | Residual token distributions | Built-in `evaluate` and research detectors |

---

## Defensive Security Architecture

All file processing follows defensive security controls:
- **Zip Bomb Defense**: Enforces maximum decompression ratio limits ($100\times$) and uncompressed size ceilings ($100\text{ MB}$).
- **PDF Security Scanner**: Flags embedded `/JavaScript`, `/JS`, `/Launch`, `/EmbeddedFiles`, and `/SubmitForm` actions.
- **Macro Detection**: Flags embedded VBA macro projects (`vbaProject.bin`).
- **Path Traversal Guards**: Normalizes paths, rejects null bytes, guards against directory traversal (`../`), and protects Windows reserved device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`).
- **Atomic Output Writes**: All write operations execute via `tempfile` + `os.replace` to prevent corrupted partial writes and symlink hijacking.
- **Zero-Egress Guarantee**: All core operations run strictly offline without outbound network calls.

---

## Tests and Verification

Run the full automated test suite (90 tests across all subsystems):

```bash
# Run pytest across the entire repository
python -m pytest tests/ -v
```

```text
============================== 90 passed in 6.19s =============================
```

---

## Changelog

### [2.0.0] - 2026-08-16
- **Universal Agent Ecosystem**: Added native agent skills and workspace rules for **Antigravity IDE** (`.agents/`), **Claude Desktop**, **Cursor** (`.cursor/`), **OpenAI Codex**, and **Grok** with a single unified installer (`python install_skill.py --target all`).
- **Multimedia Sanitization (`claudemark/provenance/multimedia.py`)**: Added ISOBMFF and ID3v2 parsers to strip metadata atoms and tags from `.mp4`, `.mov`, `.m4a`, and `.mp3` containers.
- **Interactive Side-by-Side HTML Diff**: Added `claudemark diff --html -o report.html` generating visual dark-mode comparison tables.
- **JSON Schema Export**: Added `claudemark schema` command for external agent tool calling and API contracts.
- **Concurrent Directory Auditing**: ThreadPoolExecutor parallelized recursive audit engine.
- **Native AVIF & HEIC Stripping**: ISOBMFF parser for `.avif` and `.heic` containers.
- **Defensive Container Security Scanner**: Scanning for zip bombs, malicious PDF actions, macros, and path traversal.
- **Zero-Egress Hardening**: 100% verified offline CPU execution.
- **Test Suite**: Expanded to 90 tests with 100% pass rate.

### [1.0.0] - 2026-08-16
- Initial release of ClaudeMark multi-AI statistical detector suite, document/image sanitizers, web dashboard, and REST API.

---

## Ethics and Responsible Research

ClaudeMark is intended for privacy, hygiene, and forensic research on content **you own or have authorization to process**.

1. **Probabilistic Nature**: Statistical detection is based on mathematical regularities and does not constitute definitive proof of AI generation.
2. **Disruption vs. Erasure**: Disruption rewriting is experimental and does not guarantee complete signal removal.
3. **No Vendor Secrets**: Algorithms are derived from open, peer-reviewed scientific literature.

---

## License

ClaudeMark is licensed under the [MIT License](LICENSE). Created by [Karthik R Shet](https://github.com/karthikrshet).

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
