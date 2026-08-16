# Contributing to ClaudeMark

Thank you for your interest in contributing to **ClaudeMark**! We welcome bug reports, feature suggestions, detector algorithms, provenance cleaners, and documentation improvements.

---

## 🛠️ Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/<your-username>/ClaudeMark.git
cd ClaudeMark

# 2. Set up virtual environment
python -m venv .venv
# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install development requirements
pip install -r requirements-dev.txt

# 4. Run the full test suite
python -m pytest tests/
```

---

## 📜 Scientific & Ethical Guidelines

1. **Zero-Egress by Default**: Core detectors, cleaners, and analyzers must operate 100% locally on user hardware without outbound telemetry or unauthorized API calls.
2. **Scientific Transparency**: Do not claim that heuristics prove definitive authorship or guarantee watermark removal. Clearly document assumptions, minimum text lengths, and false-positive risks.
3. **Pluggable Architecture**: Implement new detectors using `WatermarkDetector` and register them in `detector_registry`. Implement pixel backends using `PixelWatermarkBackend`.
4. **Defensive Processing**: Treat all incoming files as potentially untrusted input. Use `validate_safe_path()` and avoid shell executions.
5. **Comprehensive Tests**: Every new feature, cleaner, or detector must include unit tests. Ensure all tests pass with `python -m pytest tests/`.
