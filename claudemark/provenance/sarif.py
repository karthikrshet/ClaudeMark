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


def convert_audit_report_to_sarif(report: DirectoryAuditReport) -> dict[str, Any]:
    """Convert ClaudeMark audit report into standard OASIS SARIF v2.1.0 format."""
    results = []

    for f in report.findings:
        rule_id = "CM002-C2PATrackingManifest"
        level = "warning"

        if "Unicode" in f.finding_type or "Steganography" in f.finding_type:
            rule_id = "CM001-ZeroWidthSteganography"
            level = "error"
        elif "Security" in f.finding_type or "Bomb" in f.finding_type or "Macro" in f.finding_type:
            rule_id = "CM004-ContainerSecurityThreat"
            level = "error"
        elif "Statistical" in f.finding_type or "Watermark" in f.finding_type:
            rule_id = "CM003-HighStatisticalAnomaly"
            level = "note"

        rel_path = f.file_path
        try:
            rel_path = str(Path(f.file_path).relative_to(Path.cwd()))
        except Exception:
            pass

        results.append({
            "ruleId": rule_id,
            "level": level,
            "message": {
                "text": f"[{f.finding_type}] {f.details}"
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": rel_path.replace("\\", "/"),
                            "uriBaseId": "%SRCROOT%"
                        },
                        "region": {
                            "startLine": 1,
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


def export_sarif(report: DirectoryAuditReport, output_path: Path) -> Path:
    """Save SARIF 2.1.0 report to disk."""
    sarif_data = convert_audit_report_to_sarif(report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(sarif_data, indent=2), encoding="utf-8")
    return output_path
