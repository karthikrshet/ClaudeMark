# Changelog

All notable changes to **ClaudeMark** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.2.0] - 2026-08-17

### Reliability & Production Hardening
- **9-Point Self-Test Diagnostic (`claudemark selftest`)**: Added comprehensive release-gate diagnostic testing imports, detectors, Unicode forensics, rewrite engine, agent registry, atomic writes, security scanner, SARIF compliance, and zero-egress isolation (`python claudemark.py selftest`).
- **CLI Escaped Unicode Support (`--text-escaped`)**: Added `--text-escaped` across `analyze`, `unicode`, `rewrite`, and `normalize` commands, enabling robust handling of literal `\u200b` escape sequences in Windows Command Prompt (`cmd.exe`).
- **Standardized REST API Contracts (`claudemark/server.py`)**: Unified response and error envelopes with `ok`, `schema_version="1.0"`, `tool`, `result`/`error`, and unique `request_id`; added `GET /ready`, `GET /version`, and `GET /favicon.ico` (204 No Content).
- **Resilient AI Agent Dispatch (`claudemark/agent/`)**: Flexible payload support in `/api/agent/exec` and CLI `agent exec` with allowlist tool validation and fallback quote parsing.
- **Forensic False-Positive Elimination (`claudemark/provenance/documents.py`, `audit.py`)**: Strict differentiation between binary embedded C2PA manifests (`CONFIRMED`) and textual documentation references (`INFORMATIONAL`), eliminating false alarms on repository markdown files.
- **Calibrated Scientific Benchmarks (`claudemark/core/benchmarks.py`, `claudemark/watermark/experimental.py`)**: Multi-sentence representative human/AI corpora for reproducible statistical benchmarking and threshold calibration sweeps with non-empty dataset validation.
- **Path Operations Hardening (`claudemark/provenance/base.py`, `audit.py`)**: Refactored `safe_atomic_write_bytes` and `audit_directory` to operate strictly on validated `Path` objects, eliminating CodeQL taint warnings.

---

## [2.1.1] - 2026-08-17

### Security & Hardening
- **Taint-Chain Breaking Path Sanitizer (`claudemark/provenance/base.py`)**: Added `_sanitize_raw_path()` with strict control character and null-byte denial to satisfy CodeQL taint analysis across all filesystem operations.
- **Multimedia Path Sanitization (`claudemark/provenance/multimedia.py`)**: Sanitized all path handling in audio/video container inspection and cleaning routines.
- **Docker Container Hardening (`Dockerfile`)**: Configured unprivileged non-root user (`cmuser`), added container `HEALTHCHECK`, and aligned internal port mapping.
- **Configurable Server CORS (`claudemark/server.py`)**: Added `CLAUDEMARK_CORS_ORIGIN` environment variable support to restrict cross-origin access in production environments.

### Fixed
- **CLI Standard Options (`claudemark/cli.py`)**: Added top-level `--version` / `-V` flag; added `claudemark agent tools` alias for `agent list`; enabled flexible `agent exec` argument parsing.
- **JSON Report Versioning (`claudemark/reports/json_report.py`)**: Dynamically references package `__version__` instead of static placeholder.
- **API Ergonomics & Field Aliases**: Added `composite_score` alias to `DetectionResult` and `WatermarkResult` objects; added `normalize_text_str()` convenience helper in top-level package.
- **Rewrite Disruption Engine (`claudemark/rewrite/`)**: Vastly expanded curated synonym vocabulary across academic, transition, and verbal inflections; updated cadence rebalancer and metric calculations (`words_changed`, `characters_changed`).
- **OASIS SARIF Exporter (`claudemark/provenance/sarif.py`)**: Added `build_sarif_report()` alias and polymorphic input support for both `DirectoryAuditReport` objects and findings lists.
- **Pixel Domain Module (`claudemark/pixel/backends.py`)**: Created module export to ensure `import claudemark.pixel.backends` functions seamlessly.

---

## [2.1.0] - 2026-08-17

### Added
- **OASIS SARIF v2.1.0 Exporter**: GitHub Code Scanning and Security alerts integration for recursive forensic audits (`claudemark audit --sarif report.sarif`).
- **Diagnostic Doctor (`claudemark doctor`)**: Comprehensive runtime health, binary availability, decoder integrity, and zero-egress validation check.
- **Reproducible Scientific Benchmarks (`claudemark benchmark --reproduce`)**: Deterministic accuracy, precision, recall, and F1-score evaluation matrix across heuristic detectors.
- **Sentence-Level Heatmap Forensics (`claudemark/core/text_stats.py`)**: Sentence-by-sentence statistical score visualization with contextual anomaly badges (`CLEAN`, `ELEVATED`, `HIGH`).
- **Cryptographic Audit Certificate (`claudemark/provenance/certificate.py`)**: Standalone self-contained HTML/JSON forensic report generation with SHA-256 integrity digest.
- **PyPI Packaging (`pyproject.toml`)**: Standardized PEP 517 / 621 packaging with console scripts and optional extras (`all`, `images`, `documents`, `dev`).
- **GitHub Actions & Pre-commit Hooks**: Official GitHub Action (`action.yml`) and `.pre-commit-hooks.yaml` for automated PR forensic scanning.

---

## [2.0.0] - 2026-08-16

- **Native AVIF & HEIC Stripping (`claudemark/provenance/images.py`)**: Built-in standard library ISOBMFF box parser for `.avif` and `.heic` containers stripping `c2pa`, `Exif`, and `xml ` metadata boxes with atomic file replacement.
- **Recursive Forensic Tree Audit (`claudemark/provenance/audit.py`)**: Added `claudemark audit [dir]` command for recursive directory auditing with finding confidence ratings (`confirmed`, `probable`, `informational`).
- **Cursor Rule & Skill Installer**: Added `.cursor/rules/clean-user-facing-text.mdc` and cross-platform `install_skill.py`.
- **Automated Research Bootstraps**: One-click scripts (`scripts/setup_synthid.*`, `scripts/setup_ctrlregen.*`) for optional GPU harnesses.
- **Unicode Forensics Subsystem**: Added `visualize_unicode_markers()` supporting ZWSP, ZWNJ, ZWJ, WJ, BOM, MVS, Tags, Variation Selectors, BiDi overrides, and Latin-confusable homoglyphs with visual tags (`<ZWSP>`, `<BOM>`, `<RLO>`).
- **Statistical Disruption Rewrite Lab (`claudemark/rewrite/`)**: Best-effort statistical watermark disruption via synonym substitution, cadence rebalancing, before/after score tracking, and semantic similarity measurement.
- **Pixel-Domain Watermark Research Framework (`claudemark/pixel/`)**: Standardized adapters and registry for SynthID-Image, CtrlRegen, MarkDiffusion, Tree-Ring, Stable Signature, and StegaStamp with honest availability reporting.
- **C2PA Provenance Hierarchy Builder**: Manifest parsing, claim generator extraction, software agent detection, actions, assertions, and human-readable ASCII provenance trees.
- **Defensive Container Security Scanner (`claudemark/security/`)**: Scanning for zip decompression bombs ($100\times$ ratio caps), malicious PDF actions (`/JavaScript`, `/Launch`), macro detection (`vbaProject.bin`), and path traversal guards.
- **Atomic File Replacement**: Hardened `safe_atomic_write_bytes()` and `safe_atomic_write_text()` preventing symlink redirection and corrupted writes.
- **HTTP Bearer Auth**: Integrated `CLAUDEMARK_SERVER_API_KEY` token enforcement.
- **AI Agent Integration (`claudemark/agent/`)**: JSON schema tool manifest and local zero-egress tool execution dispatcher.
- **Expanded CLI**: Subcommands `unicode`, `rewrite`, `evaluate`, `security`, `c2pa`, `audit`, and `agent`.
- **Expanded REST API**: `/api/unicode/analyze`, `/api/unicode/visualize`, `/api/rewrite`, `/api/evaluate`, `/api/security/scan`, `/api/agent/*`.
- **Zero-Egress Test Suite**: Socket interceptor test verifying 0 network calls during offline operations.

### Changed
- Refactored server file sandboxing to use whitelisted extension mappings and static sandbox paths, resolving all CodeQL path injection alerts.
- Reconciled documentation across `README.md`, `AUDIT.md`, `SECURITY.md`, `CONTRIBUTING.md`, and `RELEASE_READINESS.md`.

---

## [1.0.0] - 2026-08-16

### Initial Release
- Multi-AI statistical text analysis (Claude research detector, Kirchenbauer z-score detector, SynthID-style adapter, generic detector).
- File provenance and metadata stripping across 10 document and image formats.
- Glassmorphic dark-mode web dashboard and REST API.
- Comprehensive test suite and benchmark framework.
