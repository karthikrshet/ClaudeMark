```
 ____ _                 _      __  __            _    
/ ___| | __ _ _   _  __| | ___|  \/  | __ _ _ __| | __
| |   | |/ _` | | | |/ _` |/ _ \ |\/| |/ _` | '__| |/ /
| |___| | (_| | |_| | (_| |  __/ |  | | (_| | |  |   < 
 \____|_|\__,_|\__,_|\__,_|\___|_|  |_|\__,_|_|  |_|\_\
```

# ClaudeMark

[![CI](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml/badge.svg)](https://github.com/karthikrshet/ClaudeMark/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/releases)
[![Stars](https://img.shields.io/github/stars/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/stargazers)
[![Forks](https://img.shields.io/github/forks/karthikrshet/ClaudeMark)](https://github.com/karthikrshet/ClaudeMark/forks)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Local-first multi-AI watermark detection, provenance forensics, document sanitization, statistical disruption rewriting, and container security platform for content you own.

| Layer | Target | Mechanism |
| --- | --- | --- |
| **Layer A (Deterministic)** | Invisible Unicode, ZWSP, ZWNJ, ZWJ, WJ, BOM, MVS, Unicode Tags, Variation Selectors, BiDi overrides, exotic spaces, homoglyphs | Linear-time token analysis, NFC normalization, steganography visualization (`<ZWSP>`, `<BOM>`, `<RLO>`) |
| **Layer B (Statistical Text)** | Statistical token bias, transition regularity, entropy modulation, Kirchenbauer red/green list bias | Pluggable research detectors (Claude, Kirchenbauer, SynthID-style, Generic) + best-effort disruption rewriting |
| **Files & Containers** | C2PA manifests, JUMBF containers, EXIF, XMP, IPTC, document XML streams, generator signatures | Structural metadata stripping for PNG, JPEG, WebP, SVG, AVIF, HEIC, PDF, DOCX, ODT, HTML, Markdown |
| **Security & Safety** | Decompression bombs, malicious PDF actions, executable VBA macros, path traversal | Zip compression ratio limits (100x), action scanning (`/JavaScript`, `/Launch`), macro detection (`vbaProject.bin`) |
| **Pixel Domain (Research)** | Latent and spatial image watermarks | Standardized research adapters for SynthID-Image, CtrlRegen, MarkDiffusion, Tree-Ring, Stable Signature, StegaStamp |

Vendors and ecosystems evaluated: **Claude (Anthropic research heuristics)**, **Gemini / SynthID-Text**, **OpenAI provenance surfaces**, **open-LLM Kirchenbauer-class schemes**.

**Latest release:** [v2.0.0](https://github.com/karthikrshet/ClaudeMark/releases/tag/v2.0.0)  
**Author & Maintainer:** [Karthik R Shet](https://github.com/karthikrshet)  
**Repository:** [https://github.com/karthikrshet/ClaudeMark](https://github.com/karthikrshet/ClaudeMark)

---

## Quick Use (CLI)

```bash
# 1. Text Analysis (Statistical watermark signal + Unicode anomalies)
python claudemark.py analyze sample.txt --algorithm claude --verbose
python claudemark.py analyze sample.txt --algorithm kirchenbauer --json

# 2. Unicode Forensics (Inspect, Visualize, Clean)
python claudemark.py unicode inspect draft.txt
python claudemark.py unicode visualize draft.txt      # Exposes <ZWSP>, <BOM>, <RLO>, etc.
python claudemark.py unicode clean draft.txt -o clean.txt

# 3. Statistical Disruption & Rewrite Lab (Best-effort restructuring)
python claudemark.py rewrite draft.txt -o rewritten.txt --strategy synonym_cadence
python claudemark.py evaluate draft.txt rewritten.txt # Measures score shift, semantic similarity, entropy delta

# 4. File Provenance & Sanitization (10 formats)
python claudemark.py inspect document.pdf
python claudemark.py clean document.pdf -o clean.pdf
python claudemark.py inspect photo.png
python claudemark.py clean photo.png -o clean_photo.png

# 5. C2PA Hierarchy & Provenance Trees
python claudemark.py c2pa inspect image.jpg

# 6. Defensive Security Scanner
python claudemark.py security scan upload.pdf

# 7. AI Agent Tool Dispatcher (Local & zero-egress)
python claudemark.py agent list
python claudemark.py agent exec analyze_watermark --args '{"text":"Sample text", "algorithm":"claude"}'

# 8. Start Local Web Dashboard & REST API
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
| `POST` | `/api/agent/tools` | None | Lists available agent tool definitions in JSON schema |
| `POST` | `/api/agent/exec` | `{"tool_name": "...", "arguments": {...}}` | Executes agent tool invocation locally |

```bash
# Health check
curl -s http://127.0.0.1:8765/health

# Analyze text via REST
curl -s -X POST http://127.0.0.1:8765/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "In conclusion, comprehensive paradigms are essential.", "algorithm": "claude"}'
```

---

## Docker and Compose Infrastructure

Run ClaudeMark inside an isolated container with read-only root filesystems and non-root execution:

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

## Environment Configuration

Configuration variables are supported via environment exports or a local `.env` file (gitignored by default):

| Variable | Target | Purpose |
| --- | --- | --- |
| `CLAUDEMARK_PORT` | HTTP Server | Port to bind server (default: `8765`) |
| `CLAUDEMARK_HOST` | HTTP Server | Interface to bind (default: `127.0.0.1` loopback) |
| `CLAUDEMARK_MAX_INPUT_BYTES` | File processing | Maximum allowed input payload (default: `104857600` / 100 MB) |
| `CLAUDEMARK_REWRITE_SEED` | Rewrite Engine | Deterministic seed for reproducible local synonym rotation |

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
- **Zero-Egress Guarantee**: All core operations run strictly offline without outbound network calls.

---

## Tests and Verification

Run the full automated test suite (79 tests across all subsystems):

```bash
# Run pytest across the entire repository
python -m pytest tests/ -v
```

```text
============================== 79 passed in 5.42s =============================
```

---

## Changelog

### [2.0.0] - 2026-08-16
- **Unicode Forensics**: Added `visualize_unicode_markers()` for human-readable tag rendering (`<ZWSP>`, `<BOM>`, `<RLO>`).
- **Rewrite Lab (`claudemark/rewrite/`)**: Best-effort statistical watermark disruption, synonym substitution, cadence rebalancing, and before/after evaluation.
- **Pixel Research Framework (`claudemark/pixel/`)**: Standardized adapters for SynthID-Image, CtrlRegen, MarkDiffusion, Tree-Ring, Stable Signature, and StegaStamp.
- **C2PA Hierarchy**: Provenance tree extraction with claim generator, software agent, and action parsing.
- **Security Scanner (`claudemark/security/`)**: Defensive scanner for zip bombs, malicious PDF actions, macros, and path traversal.
- **AI Agent Tools (`claudemark/agent/`)**: JSON schema tool definitions and local execution dispatcher.
- **Test Suite**: Expanded to 79 tests with 100% pass rate.

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
