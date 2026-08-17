"""Concurrent multi-threaded directory and website forensic audit engine for ClaudeMark.

Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .base import validate_safe_path
from .documents import inspect_document
from .images import inspect_image_file
from .multimedia import inspect_multimedia_file
from ..core.unicode_forensics import analyze_unicode_forensics
from ..detectors.registry import detector_registry
from ..security.scanner import scan_file_security


@dataclass
class FindingItem:
    """Individual forensic finding with confidence classification."""
    file_path: str
    finding_type: str
    confidence: str  # 'confirmed' | 'probable' | 'informational' | 'likely_false_positive'
    details: str


@dataclass
class DirectoryAuditReport:
    """Aggregate audit report for a recursive directory tree."""
    directory_path: str
    total_files_scanned: int = 0
    total_suspicious_files: int = 0
    total_unicode_anomalies: int = 0
    total_c2pa_manifests: int = 0
    total_security_threats: int = 0
    findings: list[FindingItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        res = asdict(self)
        res["findings"] = [asdict(f) for f in self.findings]
        return res


def _audit_single_file(file_path: Path) -> tuple[bool, int, int, int, list[FindingItem]]:
    """Audit single file returning (is_suspicious, unicode_anomalies, c2pa_count, security_threats, findings)."""
    ext = file_path.suffix.lower()
    is_suspicious = False
    unicode_anomalies = 0
    c2pa_count = 0
    security_threats = 0
    findings: list[FindingItem] = []

    # 1. Document & Text inspection
    if ext in (".txt", ".md", ".markdown", ".html", ".htm", ".pdf", ".docx", ".odt"):
        try:
            doc_rep = inspect_document(file_path)
            if doc_rep.suspicious:
                is_suspicious = True
            unicode_anomalies += doc_rep.unicode_anomalies
            if doc_rep.has_c2pa:
                c2pa_count += 1
                findings.append(FindingItem(
                    file_path=str(file_path),
                    finding_type="C2PA_MANIFEST",
                    confidence="confirmed",
                    details="Hard-bound C2PA Content Credentials found",
                ))
            if doc_rep.unicode_anomalies > 0:
                findings.append(FindingItem(
                    file_path=str(file_path),
                    finding_type="UNICODE_STEGANOGRAPHY",
                    confidence="confirmed",
                    details=f"Detected {doc_rep.unicode_anomalies} zero-width / steganographic characters",
                ))
        except Exception:
            pass

    # 2. Image inspection
    elif ext in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".avif", ".heic", ".heif"):
        try:
            img_rep = inspect_image_file(file_path)
            if img_rep.suspicious:
                is_suspicious = True
            if img_rep.has_c2pa:
                c2pa_count += 1
                findings.append(FindingItem(
                    file_path=str(file_path),
                    finding_type="IMAGE_C2PA",
                    confidence="confirmed",
                    details="C2PA JUMBF / metadata chunk present in image",
                ))
        except Exception:
            pass

    # 3. Multimedia inspection
    elif ext in (".mp4", ".mov", ".m4a", ".mp3"):
        try:
            med_rep = inspect_multimedia_file(file_path)
            if med_rep.suspicious:
                is_suspicious = True
            if med_rep.has_c2pa:
                c2pa_count += 1
                findings.append(FindingItem(
                    file_path=str(file_path),
                    finding_type="MULTIMEDIA_C2PA",
                    confidence="confirmed",
                    details="C2PA atom present in multimedia container",
                ))
        except Exception:
            pass

    # 4. Defensive security scan on containers
    if ext in (".pdf", ".docx", ".odt", ".zip"):
        try:
            sec_rep = scan_file_security(file_path)
            if not sec_rep.is_safe:
                security_threats += 1
                is_suspicious = True
                findings.append(FindingItem(
                    file_path=str(file_path),
                    finding_type="SECURITY_THREAT",
                    confidence="confirmed",
                    details="; ".join(sec_rep.warnings),
                ))
        except Exception:
            pass

    return is_suspicious, unicode_anomalies, c2pa_count, security_threats, findings


def audit_directory(
    directory_path: Path | str,
    max_files: int = 1000,
    max_workers: int = 8,
) -> DirectoryAuditReport:
    """Recursively audit all supported files in a directory tree with parallel worker threads."""
    root_dir = validate_safe_path(directory_path)
    if not root_dir.is_dir():
        raise NotADirectoryError(f"Target is not a valid directory: {root_dir}")

    report = DirectoryAuditReport(directory_path=str(root_dir))
    collected_files: list[Path] = []

    # Safely gather files within containment boundary using Path.rglob
    for p in root_dir.rglob("*"):
        if len(collected_files) >= max_files:
            break
        # Skip directories and hidden git/virtualenv metadata folders
        if p.is_file():
            parts = p.parts
            if any(part.startswith(".") and part not in (".cursor", ".claude", ".agents", ".grok", ".codex") for part in parts):
                continue
            if "node_modules" in parts or "__pycache__" in parts or ".venv" in parts or "venv" in parts:
                continue
            try:
                safe_file = validate_safe_path(p, base_dir=root_dir)
                collected_files.append(safe_file)
            except Exception:
                continue

    report.total_files_scanned = len(collected_files)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_audit_single_file, f): f for f in collected_files}
        for future in as_completed(futures):
            try:
                is_susp, u_anom, c2pa_c, sec_t, f_list = future.result()
                if is_susp:
                    report.total_suspicious_files += 1
                report.total_unicode_anomalies += u_anom
                report.total_c2pa_manifests += c2pa_c
                report.total_security_threats += sec_t
                report.findings.extend(f_list)
            except Exception:
                pass

    return report
