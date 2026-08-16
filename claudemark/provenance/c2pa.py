"""C2PA manifest detection, extraction, provenance tree generation, and verification.

Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Magic signatures for C2PA JUMBF boxes
C2PA_JUMBF_UUID = b"\x63\x32\x70\x61"  # "c2pa"
C2PA_BOX_TYPE = b"c2pa"
C2PA_MANIFEST_URN = b"urn:c2pa:"

_CLAIM_GENERATOR_RE = re.compile(rb'"claim_generator":\s*"([^"]+)"')
_SOFTWARE_AGENT_RE = re.compile(rb'"softwareAgent":\s*"([^"]+)"')
_ACTION_NAME_RE = re.compile(rb'"action":\s*"([^"]+)"')


@dataclass
class C2PAProvenanceTree:
    """Structured hierarchical representation of an asset's provenance."""
    asset_name: str
    status: str  # "PRESENT", "VALID", "INVALID", "UNVERIFIED", "ABSENT"
    manifest_urn: str = ""
    claim_generator: str = ""
    software_agent: str = ""
    actions: list[str] = field(default_factory=list)
    ingredients: list[str] = field(default_factory=list)
    assertions: list[str] = field(default_factory=list)
    signature_info: dict[str, Any] = field(default_factory=dict)
    tree_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def inspect_c2pa_bytes(data: bytes, asset_name: str = "Asset") -> dict[str, Any]:
    """Scan raw bytes for embedded C2PA JUMBF containers, assertions, and metadata."""
    has_c2pa = (
        C2PA_JUMBF_UUID in data or
        C2PA_BOX_TYPE in data or
        C2PA_MANIFEST_URN in data or
        b"c2pa.assertions" in data or
        b"c2pa.signature" in data
    )

    if not has_c2pa:
        tree = C2PAProvenanceTree(
            asset_name=asset_name,
            status="ABSENT",
            tree_text=f"{asset_name}\n └── (No C2PA manifest found)",
        )
        return {
            "has_c2pa": False,
            "status": "ABSENT",
            "method": "byte_scan",
            "indicators": [],
            "provenance_tree": tree.to_dict(),
        }

    # Extract claims
    claim_gen = ""
    gen_match = _CLAIM_GENERATOR_RE.search(data)
    if gen_match:
        claim_gen = gen_match.group(1).decode("utf-8", errors="replace")

    software_agent = ""
    agent_match = _SOFTWARE_AGENT_RE.search(data)
    if agent_match:
        software_agent = agent_match.group(1).decode("utf-8", errors="replace")

    actions: list[str] = []
    for m in _ACTION_NAME_RE.finditer(data):
        act = m.group(1).decode("utf-8", errors="replace")
        if act not in actions:
            actions.append(act)

    indicators: list[str] = []
    assertions: list[str] = []
    if b"c2pa.assertions" in data:
        indicators.append("C2PA Assertion Manifest")
        assertions.append("c2pa.assertions")
    if b"c2pa.actions" in data:
        assertions.append("c2pa.actions")
    if b"c2pa.hash.data" in data:
        assertions.append("c2pa.hash.data")
    if b"c2pa.signature" in data:
        indicators.append("Cryptographic Provenance Signature")
    if b"stds.schema-org.CreativeWork" in data:
        indicators.append("Schema.org Attribution Claims")
        assertions.append("stds.schema-org.CreativeWork")

    # Format human-readable ASCII provenance tree
    lines = [f"{asset_name}", " └── C2PA Manifest (JUMBF Container)"]
    if claim_gen:
        lines.append(f"      ├── Claim Generator: {claim_gen}")
    if software_agent:
        lines.append(f"      ├── Software Agent: {software_agent}")
    if actions:
        lines.append(f"      ├── Recorded Actions: {', '.join(actions)}")
    if assertions:
        lines.append(f"      └── Assertions: {', '.join(assertions)}")
    else:
        lines.append("      └── Signature: Cryptographic envelope detected (UNVERIFIED)")

    tree_text = "\n".join(lines)

    tree = C2PAProvenanceTree(
        asset_name=asset_name,
        status="UNVERIFIED",  # Unverified until c2patool or public key checks are run
        claim_generator=claim_gen,
        software_agent=software_agent,
        actions=actions,
        assertions=assertions,
        tree_text=tree_text,
    )

    return {
        "has_c2pa": True,
        "status": "UNVERIFIED",
        "method": "byte_scan",
        "indicators": indicators,
        "claim_generator": claim_gen,
        "software_agent": software_agent,
        "actions": actions,
        "assertions": assertions,
        "provenance_tree": tree.to_dict(),
    }


def inspect_c2pa_tool(file_path: Path) -> dict[str, Any] | None:
    """Use c2patool if available on the system for full cryptographic verification."""
    tool = shutil.which("c2patool")
    if not tool or not file_path.is_file():
        return None

    try:
        proc = subprocess.run(
            [tool, str(file_path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout:
            parsed = json.loads(proc.stdout)
            return {
                "has_c2pa": True,
                "status": "VALID",
                "method": "c2patool",
                "manifest_data": parsed,
            }
        return {
            "has_c2pa": True,
            "status": "INVALID",
            "method": "c2patool",
            "error": proc.stderr.strip() or "Manifest verification failed",
        }
    except Exception as ex:
        return {"has_c2pa": False, "status": "UNVERIFIED", "error": str(ex)}
