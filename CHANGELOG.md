# Changelog

All notable changes to **ClaudeMark** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-08-16

### Added
- **Unicode Forensics Subsystem**: Added `visualize_unicode_markers()` supporting ZWSP, ZWNJ, ZWJ, WJ, BOM, MVS, Tags, Variation Selectors, BiDi overrides, and Latin-confusable homoglyphs with visual tags (`<ZWSP>`, `<BOM>`, `<RLO>`).
- **Statistical Disruption Rewrite Lab (`claudemark/rewrite/`)**: Best-effort statistical watermark disruption via synonym substitution, cadence rebalancing, before/after score tracking, and semantic similarity measurement.
- **Pixel-Domain Watermark Research Framework (`claudemark/pixel/`)**: Standardized adapters and registry for SynthID-Image, CtrlRegen, MarkDiffusion, Tree-Ring, Stable Signature, and StegaStamp with honest availability reporting.
- **C2PA Provenance Hierarchy Builder**: Manifest parsing, claim generator extraction, software agent detection, actions, assertions, and human-readable ASCII provenance trees.
- **Defensive Container Security Scanner (`claudemark/security/`)**: Scanning for zip decompression bombs ($100\times$ ratio caps), malicious PDF actions (`/JavaScript`, `/Launch`), macro detection (`vbaProject.bin`), and path traversal guards.
- **AI Agent Integration (`claudemark/agent/`)**: JSON schema tool manifest and local zero-egress tool execution dispatcher.
- **Expanded CLI**: Subcommands `unicode`, `rewrite`, `evaluate`, `security`, `c2pa`, and `agent`.
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
