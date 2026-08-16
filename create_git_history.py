"""Script to initialize clean git repository and construct 20 meaningful commits for ClaudeMark."""

import subprocess
from pathlib import Path

REPO_DIR = Path(r"c:\Users\karti\Downloads\watermarks-remover-main\watermarks-remover-main")


def run(cmd: list[str]) -> str:
    res = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True, check=True)
    return res.stdout.strip()


def main():
    # 1. Initialize git
    run(["git", "init", "-b", "main"])
    run(["git", "config", "user.name", "Karthik R Shet"])
    run(["git", "config", "user.email", "karthikrshet@users.noreply.github.com"])

    commits = [
        (
            ["LICENSE", "SECURITY.md", "CODE_OF_CONDUCT.md", "pytest.ini", "requirements-dev.txt", ".gitignore", ".dockerignore"],
            "feat(init): initialize ClaudeMark project structure and security policies\n\n- Add MIT License (c) 2026 Karthik R Shet\n- Configure security policy, code of conduct, and dev dependencies",
        ),
        (
            [".env.example", "compose.yaml", "Dockerfile", "Makefile"],
            "feat(infra): add Docker container configuration and environment templates\n\n- Add Dockerfile with forensic tools\n- Add Compose service configuration and Makefile automation",
        ),
        (
            ["claudemark/core/text_stats.py"],
            "feat(core): implement lexical statistics and Shannon entropy engine\n\n- Compute word and character Shannon entropy\n- Calculate Type-Token Ratio (TTR) and Hapax Legomena\n- Evaluate sentence length distribution and punctuation cadence",
        ),
        (
            ["claudemark/core/unicode_forensics.py"],
            "feat(core): add deep Unicode forensics for invisible steganography\n\n- Scan for zero-width characters (ZWSP, ZWNJ, ZWJ, BOM, Word Joiner)\n- Detect non-breaking spaces (NBSP), BiDi overrides, and Latin homoglyphs\n- Check canonical NFC/NFKC/NFD normalization forms",
        ),
        (
            ["claudemark/core/normalizer.py"],
            "feat(core): implement safe non-destructive text normalizer\n\n- Reversibly strip invisible zero-width channels\n- Normalize whitespace homoglyphs without altering visible text\n- Configurable normalization options",
        ),
        (
            ["claudemark/core/diff.py"],
            "feat(core): build forensic text diff and delta metrics calculation\n\n- Compute character deltas and anomaly reduction counts\n- Calculate text similarity ratios and statistical signal delta shifts",
        ),
        (
            ["claudemark/core/__init__.py", "tests/test_claudemark_core.py"],
            "feat(core): export core data models and add comprehensive test suite\n\n- Export TextStatistics, UnicodeForensicReport, NormalizationResult\n- Add unit tests for core statistics, forensics, and diffing",
        ),
        (
            ["claudemark/watermark/base.py", "claudemark/watermark/statistical.py", "claudemark/watermark/claude_detector.py", "claudemark/watermark/registry.py", "claudemark/watermark/experimental.py", "claudemark/watermark/__init__.py", "tests/test_claudemark_watermark.py"],
            "feat(watermark): build statistical watermark analyzer and hypothesis testing\n\n- Implement burstiness, token transition regularity, and Yule's K\n- Add Composite Deviation Z-score and p-value calculation\n- Add experimental parameter sweep harness",
        ),
        (
            ["claudemark/detectors/base.py"],
            "feat(detectors): define standardized WatermarkDetector contract\n\n- Define DetectionResult, StatisticalHypothesis, and base interface\n- Standardize detect(), analyze(), score(), explain(), and limitations()",
        ),
        (
            ["claudemark/detectors/claude.py"],
            "feat(detectors): implement Claude multi-signal research detector\n\n- Multi-dimensional scoring for structural burstiness and entropy constraints\n- Transparent scientific disclaimers and empirical hypothesis testing",
        ),
        (
            ["claudemark/detectors/kirchenbauer.py"],
            "feat(detectors): add Kirchenbauer red/green list watermark detector\n\n- Model published Kirchenbauer et al. (2023) watermarking scheme\n- Calculate green token counts, binomial z-scores, and one-tailed p-values",
        ),
        (
            ["claudemark/detectors/synthid.py", "claudemark/detectors/generic.py", "claudemark/detectors/registry.py", "claudemark/detectors/__init__.py", "tests/test_claudemark_detectors.py"],
            "feat(detectors): add SynthID research adapter and dynamic DetectorRegistry\n\n- Add SynthID-style entropy modulation research adapter\n- Add GenericEntropy baseline detector\n- Dynamic pluggable registry for all watermark algorithms",
        ),
        (
            ["claudemark/provenance/base.py", "claudemark/provenance/c2pa.py", "claudemark/provenance/exif_xmp.py"],
            "feat(provenance): implement C2PA inspection and EXIF/XMP metadata analyzer\n\n- Scan for C2PA JUMBF containers and cryptographic assertions\n- Inspect EXIF, XMP, IPTC, and AI-generator prompt footprints",
        ),
        (
            ["claudemark/provenance/documents.py", "claudemark/provenance/images.py"],
            "feat(provenance): build self-contained document and image cleaners\n\n- Clean PDF, DOCX, ODT, HTML, Markdown, and TXT containers\n- Strip metadata from PNG, JPEG, WebP, SVG, AVIF, and HEIC\n- 100% self-contained Python stdlib implementation",
        ),
        (
            ["claudemark/provenance/batch.py", "claudemark/provenance/__init__.py", "tests/test_claudemark_provenance.py", "tests/test_claudemark_batch.py"],
            "feat(provenance): add recursive batch directory inspection and cleaning\n\n- Implement batch_inspect() and batch_clean() across directory trees\n- Structured batch summary reports and tests",
        ),
        (
            ["claudemark/reports/terminal.py", "claudemark/reports/json_report.py", "claudemark/reports/markdown_report.py", "claudemark/reports/__init__.py"],
            "feat(reports): build multi-format reporting subsystem\n\n- ASCII terminal reports with visual gauge bars\n- Standardized machine-readable JSON schema\n- GitHub-flavored Markdown reports",
        ),
        (
            ["claudemark/web/static/styles.css", "claudemark/web/static/app.js", "claudemark/web/static/index.html", "claudemark/web/app.py", "claudemark/web/__init__.py"],
            "feat(web): build interactive dark-mode Web Dashboard\n\n- Single-page application with real-time text analysis\n- Drag-and-drop file inspection and document cleaning\n- Side-by-side forensic diff viewer and sample presets",
        ),
        (
            ["claudemark/server.py", "tests/test_claudemark_server.py", "tests/test_claudemark_api.py"],
            "feat(server): build self-contained local REST API server\n\n- Implement /health, /capabilities, /openapi.json\n- Implement /inspect, /clean, and /api/* JSON endpoints",
        ),
        (
            ["claudemark/cli.py", "claudemark/__main__.py", "claudemark/__init__.py", "claudemark.py", "tests/test_claudemark_cli.py"],
            "feat(cli): build unified CLI interface and root runner\n\n- Commands: analyze, inspect, clean, diff, normalize, serve, capabilities, experimental, version\n- Robust UTF-8 encoding support across Windows and POSIX shells",
        ),
        (
            [".", ".github"],
            "feat(release): ClaudeMark v1.0.0 release\n\n- Add empirical benchmark calibration harness\n- Add zero-egress security tests and high-value edge case suites\n- Configure GitHub Actions CI/CD workflows and release pipelines\n- Complete comprehensive v1.0.0 documentation",
        ),
    ]

    for paths, msg in commits:
        for p in paths:
            run(["git", "add", p])
        run(["git", "commit", "-m", msg])

    # Tag v1.0.0
    run(["git", "tag", "-a", "v1.0.0", "-m", "ClaudeMark v1.0.0 — Multi-AI Watermark & Provenance Forensics Toolkit"])

    # Configure remote
    try:
        run(["git", "remote", "add", "origin", "https://github.com/karthikrshet/ClaudeMark.git"])
    except Exception:
        run(["git", "remote", "set-url", "origin", "https://github.com/karthikrshet/ClaudeMark.git"])

    print("Successfully created 20 commits and tagged v1.0.0!")


if __name__ == "__main__":
    main()
