"""Web application backend routing and static asset handlers for ClaudeMark."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .. import analyze_text, compute_forensic_diff, normalize_text
from ..core.normalizer import NormalizationOptions
from ..reports.json_report import format_json_report
from ..watermark.registry import registry

STATIC_DIR = Path(__file__).resolve().parent / "static"


def get_static_asset(filename: str) -> tuple[bytes, str] | None:
    """Retrieve static web asset bytes and MIME content type."""
    file_map = {
        "": ("index.html", "text/html; charset=utf-8"),
        "/": ("index.html", "text/html; charset=utf-8"),
        "index.html": ("index.html", "text/html; charset=utf-8"),
        "styles.css": ("styles.css", "text/css; charset=utf-8"),
        "/static/styles.css": ("styles.css", "text/css; charset=utf-8"),
        "app.js": ("app.js", "application/javascript; charset=utf-8"),
        "/static/app.js": ("app.js", "application/javascript; charset=utf-8"),
    }

    target = file_map.get(filename.strip())
    if not target:
        if filename.startswith("/static/"):
            name = filename[len("/static/"):]
            if name in file_map:
                target = file_map[name]

    if not target:
        return None

    asset_file, mime_type = target
    path = STATIC_DIR / asset_file
    if path.is_file():
        return path.read_bytes(), mime_type
    return None


def handle_api_analyze(payload: dict[str, Any]) -> dict[str, Any]:
    """Process JSON request for text analysis."""
    text = payload.get("text", "")
    algorithm = payload.get("algorithm", "claude")
    threshold = payload.get("threshold")
    source_name = payload.get("source_name", "web_input")

    res = analyze_text(text, detector_name=algorithm, threshold=threshold)
    stats = res["text_statistics"]
    unicode_rep = res["unicode_forensics"]
    wm_res = res["watermark_result"]

    raw_json = format_json_report(stats, unicode_rep, wm_res, source_name=source_name)
    return json.loads(raw_json)


def handle_api_normalize(payload: dict[str, Any]) -> dict[str, Any]:
    """Process JSON request for safe normalization."""
    text = payload.get("text", "")
    opts = NormalizationOptions(
        strip_zero_width=payload.get("strip_zero_width", True),
        normalize_spaces=payload.get("normalize_spaces", True),
        strip_bidi_controls=payload.get("strip_bidi", True),
        strip_unprintable_controls=True,
        normalize_unicode_form=payload.get("form", "NFC"),
        replace_homoglyphs=payload.get("replace_homoglyphs", False),
        strip_bom=True,
    )
    result = normalize_text(text, options=opts)
    return result.to_dict()


def handle_api_diff(payload: dict[str, Any]) -> dict[str, Any]:
    """Process JSON request for forensic diff."""
    original = payload.get("original", "")
    processed = payload.get("processed", "")
    algorithm = payload.get("algorithm", "claude")

    detector = registry.get(algorithm)
    orig_score = detector.score(original)
    proc_score = detector.score(processed)

    diff = compute_forensic_diff(
        original,
        processed,
        original_score=orig_score,
        new_score=proc_score,
    )
    return {
        "tool": "ClaudeMark",
        "command": "diff",
        "diff": diff.to_dict(),
    }
