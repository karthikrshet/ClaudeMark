"""OASIS SARIF (Static Analysis Results Interchange Format) v2.1.0 Exporter for ClaudeMark.

Enables automated GitHub Code Scanning and Security alerts integration.
Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit import DirectoryAuditReport


RULES_METADATA = [
    {
        "id": "CM001-ZeroWidthSteganography",
        "name": "ZeroWidthSteganography",
        "shortDescription": {"text": "Hidden zero-width Unicode characters or steganographic markers detected."},
        "fullDescription": {"text": "Text contains invisible zero-width spaces, BiDi overrides, or steganographic character sequences that may be used for tracking or prompt injection."},
        "defaultConfiguration": {"level": "error"},
        "helpUri": "https://github.com/karthikrshet/ClaudeMark#unicode--steganography-forensics",
    },
    {
        "id": "CM002-C2PATrackingManifest",
        "name": "C2PATrackingManifest",
        "shortDescription": {"text": "C2PA provenance manifest or generative AI tracking signature present."},
        "fullDescription": {"text": "Document or image container embeds C2PA assertion manifests, watermarks, or origin claim signatures."},
        "defaultConfiguration": {"level": "warning"},
        "helpUri": "https://github.com/karthikrshet/ClaudeMark#c2pa--provenance-inspection",
    },
    {
        "id": "CM003-HighStatisticalAnomaly",
        "name": "HighStatisticalAnomaly",
        "shortDescription": {"text": "Elevated statistical AI watermark bias detected in text."},
        "fullDescription": {"text": "Text exhibits high generative sampling regularities or green-list token distributions consistent with LLM watermarking."},
        "defaultConfiguration": {"level": "note"},
        "helpUri": "https://github.com/karthikrshet/ClaudeMark#multi-model-detector-zoo",
    },
    {
        "id": "CM004-ContainerSecurityThreat",
        "name": "ContainerSecurityThreat",
        "shortDescription": {"text": "Malicious PDF action, decompression bomb, or macro vulnerability detected."},
        "fullDescription": {"text": "Container scan flagged security risks such as high compression ratio zip bombs, embedded JavaScript in PDF, or executable macros."},
        "defaultConfiguration": {"level": "error"},
        "helpUri": "https://github.com/karthikrshet/ClaudeMark#defensive-security-scanner",
    },
]


def convert_audit_report_to_sarif(report: DirectoryAuditReport | list[dict[str, Any]] | dict[str, Any]) -> dict[str, Any]:
    """Convert ClaudeMark audit report into standard OASIS SARIF v2.1.0 format."""
    results = []

    # Handle both DirectoryAuditReport objects and raw findings lists/dicts
    findings_list = []
    if isinstance(report, DirectoryAuditReport):
        findings_list = report.findings
    elif isinstance(report, dict):
        findings_list = report.get("findings", [])
    elif isinstance(report, list):
        findings_list = report

    for f in findings_list:
        rule_id = "CM002-C2PATrackingManifest"
        level = "warning"

        finding_type = getattr(f, "finding_type", None) or (f.get("finding_type") if isinstance(f, dict) else "")
        details = getattr(f, "details", None) or (f.get("details") if isinstance(f, dict) else "")
        file_path = getattr(f, "file_path", None) or (f.get("file_path") or f.get("file") if isinstance(f, dict) else "unknown")
        line_num = getattr(f, "line_number", None) or (f.get("line") or f.get("line_number") if isinstance(f, dict) else 1)

        if "Unicode" in finding_type or "Steganography" in finding_type:
            rule_id = "CM001-ZeroWidthSteganography"
            level = "error"
        elif "Security" in finding_type or "Bomb" in finding_type or "Macro" in finding_type:
            rule_id = "CM004-ContainerSecurityThreat"
            level = "error"
        elif "Statistical" in finding_type or "Watermark" in finding_type:
            rule_id = "CM003-HighStatisticalAnomaly"
            level = "note"

        rel_path = str(file_path)
        try:
            rel_path = str(Path(file_path).relative_to(Path.cwd()))
        except Exception:
            pass

        results.append({
            "ruleId": rule_id,
            "level": level,
            "message": {
                "text": f"[{finding_type}] {details}" if finding_type else str(details or "Audit finding")
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": rel_path.replace("\\", "/"),
                            "uriBaseId": "%SRCROOT%"
                        },
                        "region": {
                            "startLine": max(int(line_num or 1), 1),
                            "startColumn": 1
                        }
                    }
                }
            ]
        })

    sarif_doc = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "ClaudeMark",
                        "semanticVersion": "2.1.0",
                        "informationUri": "https://github.com/karthikrshet/ClaudeMark",
                        "rules": RULES_METADATA,
                    }
                },
                "results": results
            }
        ]
    }
    return sarif_doc


def build_sarif_report(report: DirectoryAuditReport | list[dict[str, Any]] | dict[str, Any]) -> dict[str, Any]:
    """Alias for convert_audit_report_to_sarif: build standard SARIF 2.1.0 report."""
    return convert_audit_report_to_sarif(report)


def export_sarif(report: DirectoryAuditReport | list[dict[str, Any]] | dict[str, Any], output_path: Path) -> Path:
    """Save SARIF 2.1.0 report to disk."""
    sarif_data = convert_audit_report_to_sarif(report)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(sarif_data, indent=2), encoding="utf-8")
    return output_path

