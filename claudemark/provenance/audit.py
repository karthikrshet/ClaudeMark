"""Directory tree and website forensic audit engine for ClaudeMark.

Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .base import validate_safe_path
from .documents import inspect_document
from .images import inspect_image_file
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


def audit_directory(
    directory_path: Path | str,
    max_files: int = 1000,
) -> DirectoryAuditReport:
    """Recursively audit all supported files in a directory tree."""
    root_dir = validate_safe_path(directory_path)
    if not root_dir.is_dir():
        raise NotADirectoryError(f"Target is not a valid directory: {root_dir}")

    report = DirectoryAuditReport(directory_path=str(root_dir))
    scanned = 0

    for root, _, files in os.walk(str(root_dir)):
        for f_name in files:
            if scanned >= max_files:
                break

            file_path = Path(root) / f_name
            ext = file_path.suffix.lower()
            scanned += 1

            # 1. Document & Text inspection
            if ext in (".txt", ".md", ".markdown", ".html", ".htm", ".pdf", ".docx", ".odt"):
                try:
                    doc_rep = inspect_document(file_path)
                    if doc_rep.suspicious:
                        report.total_suspicious_files += 1
                    report.total_unicode_anomalies += doc_rep.unicode_anomalies
                    if doc_rep.has_c2pa:
                        report.total_c2pa_manifests += 1
                        report.findings.append(FindingItem(
                            file_path=str(file_path),
                            finding_type="C2PA_MANIFEST",
                            confidence="confirmed",
                            details="Hard-bound C2PA Content Credentials found",
                        ))
                    if doc_rep.unicode_anomalies > 0:
                        report.findings.append(FindingItem(
                            file_path=str(file_path),
                            finding_type="UNICODE_STEGANOGRAPHY",
                            confidence="confirmed",
                            details=f"Detected {doc_rep.unicode_anomalies} zero-width / steganographic characters",
                        ))
                except Exception:
                    pass

            # 2. Image inspection
            elif ext in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".avif", ".heic"):
                try:
                    img_rep = inspect_image_file(file_path)
                    if img_rep.suspicious:
                        report.total_suspicious_files += 1
                    if img_rep.has_c2pa:
                        report.total_c2pa_manifests += 1
                        report.findings.append(FindingItem(
                            file_path=str(file_path),
                            finding_type="IMAGE_C2PA",
                            confidence="confirmed",
                            details="C2PA JUMBF / metadata chunk present in image",
                        ))
                except Exception:
                    pass

            # 3. Defensive security scan on containers
            if ext in (".pdf", ".docx", ".odt", ".zip"):
                try:
                    sec_rep = scan_file_security(file_path)
                    if not sec_rep.is_safe:
                        report.total_security_threats += 1
                        report.findings.append(FindingItem(
                            file_path=str(file_path),
                            finding_type="SECURITY_THREAT",
                            confidence="confirmed",
                            details="; ".join(sec_rep.warnings),
                        ))
                except Exception:
                    pass

    report.total_files_scanned = scanned
    return report
