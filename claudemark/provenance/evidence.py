"""Tamper-evident evidence bundles for portable forensic hand-off."""

from __future__ import annotations

import hashlib
import json
import platform
import zipfile
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


try:
    _TOOL_VERSION = version("claudemark")
except PackageNotFoundError:
    _TOOL_VERSION = "2.2.0"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def create_evidence_bundle(
    target_path: Path | str,
    report: dict[str, Any],
    output_path: Path | str,
    *,
    include_original: bool = False,
) -> dict[str, Any]:
    """Create a ZIP with a canonical report and hashes for independent verification.

    The original is excluded by default so a bundle can be shared without copying
    sensitive content. When included, it is stored unmodified under ``original/``.
    """
    target = Path(target_path).resolve()
    if not target.is_file():
        raise FileNotFoundError(f"Evidence target is not a file: {target}")
    output = Path(output_path).resolve()
    if output == target:
        raise ValueError("Evidence bundle output must not replace the target file")
    output.parent.mkdir(parents=True, exist_ok=True)

    original = target.read_bytes()
    report_bytes = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8")
    manifest = {
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tool": "ClaudeMark",
        "tool_version": _TOOL_VERSION,
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "target": {"name": target.name, "sha256": _sha256(original), "size_bytes": len(original)},
        "report": {"path": "report.json", "sha256": _sha256(report_bytes)},
        "original_included": include_original,
    }
    manifest_bytes = json.dumps(manifest, sort_keys=True, indent=2).encode("utf-8")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("manifest.json", manifest_bytes)
        bundle.writestr("report.json", report_bytes)
        if include_original:
            bundle.writestr(f"original/{target.name}", original)
    return {"bundle_path": str(output), "bundle_sha256": _sha256(output.read_bytes()), "manifest": manifest}


def verify_evidence_bundle(bundle_path: Path | str) -> dict[str, Any]:
    """Verify a bundle's internal report hash and optional original-file hash."""
    path = Path(bundle_path).resolve()
    with zipfile.ZipFile(path) as bundle:
        manifest = json.loads(bundle.read("manifest.json"))
        report_valid = _sha256(bundle.read("report.json")) == manifest["report"]["sha256"]
        original_valid: bool | None = None
        if manifest.get("original_included"):
            original_valid = _sha256(bundle.read(f"original/{manifest['target']['name']}")) == manifest["target"]["sha256"]
    return {"valid": report_valid and original_valid is not False, "report_valid": report_valid, "original_valid": original_valid}
