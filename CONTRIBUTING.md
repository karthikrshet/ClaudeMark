# Contributing to ClaudeMark

Thank you for helping improve **ClaudeMark** — the multi-AI watermark research, Unicode steganography forensics, and file provenance toolkit.

---

## 👥 Roles & Governance

| Action | Who |
| :--- | :--- |
| Open issues & discussions | Anyone |
| Open pull requests | Anyone (fork the repo) |
| Suggest releases | Anyone (open a release issue) |
| Approve & merge pull requests | Maintainer only ([@karthikrshet](https://github.com/karthikrshet)) |

`main` is protected. All changes require a pull request, a passing CI test suite, and an approval from the maintainer.

---

## 💻 Development Prerequisites

- **Python 3.10+** (standard library only for core engines; no heavy dependencies required).
- From the repo root, run:
  ```bash
  python -m pytest tests/
  ```
  Ensure all tests pass before opening a PR.

---

## 🗂️ Codebase Layout

| Path | Purpose |
| :--- | :--- |
| `claudemark/core/` | Text statistics, Unicode forensics, safe normalizer, and diff engine |
| `claudemark/detectors/` | Pluggable multi-AI watermark engines (`claude`, `kirchenbauer`, `synthid`, `generic`) |
| `claudemark/provenance/` | Document & image provenance cleaners (PDF, DOCX, ODT, HTML, MD, PNG, JPEG, WebP, SVG) |
| `claudemark/reports/` | Terminal ASCII, JSON schema, and Markdown reports |
| `claudemark/web/` | Web Dashboard and static assets |
| `claudemark/server.py` | Self-contained HTTP server & REST API |
| `claudemark/cli.py` & `claudemark.py` | Unified CLI commands (`analyze`, `inspect`, `clean`, `normalize`, `diff`, `serve`, `capabilities`) |
| `tests/` | Unit and integration test suite |
| `benchmarks/` | Empirical calibration harness and datasets |

---

## ✅ Pull Request Checklist

- [ ] New feature or bug fix has corresponding tests in `tests/`.
- [ ] `python -m pytest tests/` passes cleanly with 100% success rate.
- [ ] Any new public detector or format is registered in `claudemark/detectors/` or `claudemark/provenance/`.
- [ ] Code adheres to clean, modern Python 3 typing and formatting.

---

## 🛡️ Community & Policies

- [Code of Conduct](CODE_OF_CONDUCT.md) — Community standards and expectations.
- [Security Policy](SECURITY.md) — Private vulnerability reporting.
- Author: [Karthik R Shet](https://github.com/karthikrshet)
