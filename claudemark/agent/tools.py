"""Standardized tool declarations and execution dispatcher for AI agents.

Provides local-first tool execution for Claude, OpenAI Assistants, LangChain, and Agentic frameworks.
Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .. import analyze_text, compute_forensic_diff, normalize_text
from ..core.unicode_forensics import analyze_unicode_forensics, visualize_unicode_markers
from ..detectors.registry import detector_registry
from ..provenance.batch import batch_clean, batch_inspect, clean_single_file, inspect_single_file
from ..rewrite.paraphrase import disrupt_watermark
from ..security.scanner import scan_file_security

# Standardized JSON Schema Tool Specifications
AGENT_TOOLS_MANIFEST: list[dict[str, Any]] = [
    {
        "name": "analyze_watermark",
        "description": "Analyze text for statistical AI watermarks and return structured hypotheses and scores.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text content to analyze"},
                "algorithm": {
                    "type": "string",
                    "enum": ["claude", "kirchenbauer", "synthid", "generic"],
                    "default": "claude",
                },
                "threshold": {"type": "number", "description": "Decision threshold (0.0 to 1.0)"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "analyze_unicode",
        "description": "Scan text for zero-width characters, BiDi overrides, NBSP, and Unicode steganography.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text content to inspect"},
                "visualize": {"type": "boolean", "default": True, "description": "Include human-readable visualization"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "inspect_provenance",
        "description": "Inspect a file (PDF, DOCX, PNG, JPEG, SVG, etc.) for C2PA, EXIF, XMP, and AI footprints.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the target file"},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "clean_file",
        "description": "Sanitize and strip metadata/watermarks from a document or image container.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Path to input file"},
                "output_path": {"type": "string", "description": "Path to destination file"},
            },
            "required": ["input_path"],
        },
    },
    {
        "name": "disrupt_watermark",
        "description": "Execute best-effort local statistical watermark disruption and text rebalancing.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to transform"},
                "strategy": {"type": "string", "enum": ["synonym_cadence", "cadence_only"], "default": "synonym_cadence"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "scan_security",
        "description": "Defensively scan files for zip bombs, malicious PDF actions, macros, and path traversal.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to target file"},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "get_capabilities",
        "description": "List all active detectors, supported document/image formats, and system tools.",
        "parameters": {"type": "object", "properties": {}},
    },
]


def execute_agent_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute an agent tool invocation locally with zero network egress."""
    if tool_name == "analyze_watermark":
        text = arguments.get("text", "")
        alg = arguments.get("algorithm", "claude")
        thresh = arguments.get("threshold")
        res = analyze_text(text, detector_name=alg, threshold=thresh)
        return {
            "text_statistics": res["text_statistics"].to_dict(),
            "unicode_forensics": res["unicode_forensics"].to_dict(),
            "watermark_analysis": res["watermark_result"].to_dict(),
        }

    elif tool_name == "analyze_unicode":
        text = arguments.get("text", "")
        rep = analyze_unicode_forensics(text)
        data = rep.to_dict()
        if arguments.get("visualize", True):
            data["visualized_text"] = visualize_unicode_markers(text)
        return data

    elif tool_name == "inspect_provenance":
        f_path = Path(arguments.get("file_path", "")).resolve()
        rep = inspect_single_file(f_path)
        return rep.to_dict()

    elif tool_name == "clean_file":
        in_p = Path(arguments.get("input_path", "")).resolve()
        out_p = Path(arguments.get("output_path", "")).resolve() if arguments.get("output_path") else None
        rep = clean_single_file(in_p, out_p)
        return rep.to_dict()

    elif tool_name == "disrupt_watermark":
        text = arguments.get("text", "")
        strat = arguments.get("strategy", "synonym_cadence")
        res = disrupt_watermark(text, strategy=strat)
        return res.to_dict()

    elif tool_name == "scan_security":
        f_path = Path(arguments.get("file_path", "")).resolve()
        rep = scan_file_security(f_path)
        return rep.to_dict()

    elif tool_name == "get_capabilities":
        return {
            "detectors": detector_registry.list_detectors(),
            "supported_document_formats": ["pdf", "docx", "odt", "html", "md", "txt"],
            "supported_image_formats": ["png", "jpeg", "jpg", "webp", "svg", "avif", "heic"],
            "tools": [t["name"] for t in AGENT_TOOLS_MANIFEST],
        }

    else:
        raise ValueError(f"Unknown agent tool: '{tool_name}'")
