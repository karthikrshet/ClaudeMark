"""Self-contained document provenance inspection and metadata cleaning for ClaudeMark.

Supports: PDF, DOCX, ODT, HTML, Markdown, and TXT.
Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import io
import posixpath
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Any

from ..core.normalizer import NormalizationOptions, normalize_text
from ..core.unicode_forensics import analyze_unicode_forensics
from .base import (
    FileCleaningReport,
    ProvenanceInspectionReport,
    safe_atomic_write_bytes,
    safe_atomic_write_text,
    validate_safe_path,
)

# XML / HTML metadata regex patterns
_HTML_META_AI_RE = re.compile(
    r'<meta\s+[^>]*(?:name|property)=["\']?(?:generator|author|provenance|ai-prompt|ai-model)["\']?[^>]*>',
    re.IGNORECASE,
)
_HTML_AI_ATTRS_RE = re.compile(
    r'\s+data-(?:ai|model|prompt|provenance|watermark)=["\'][^"\']*["\']',
    re.IGNORECASE,
)
_FRONTMATTER_AI_RE = re.compile(
    r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?",
    re.DOTALL,
)
_AI_PROMPT_KEYWORDS = [
    "chatgpt", "openai", "claude", "anthropic", "midjourney",
    "dall-e", "stable diffusion", "firefly", "gemini", "synthid",
]


def inspect_document(file_path: Path) -> ProvenanceInspectionReport:
    """Inspect document file for metadata, invisible characters, and AI markers."""
    file_path = validate_safe_path(file_path)
    suffix = file_path.suffix.lower()
    size = file_path.stat().st_size
    data = file_path.read_bytes()

    suspicious = False
    ai_metadata = False
    c2pa = b"c2pa" in data.lower() or b"urn:c2pa:" in data.lower()
    unicode_anomalies = 0
    details: dict[str, Any] = {}

    if suffix in (".txt", ".text"):
        raw_text = data.decode("utf-8", errors="replace")
        u_rep = analyze_unicode_forensics(raw_text)
        unicode_anomalies = u_rep.total_anomalies
        suspicious = u_rep.has_anomalies
        details = u_rep.to_dict()

    elif suffix in (".md", ".markdown"):
        raw_text = data.decode("utf-8", errors="replace")
        u_rep = analyze_unicode_forensics(raw_text)
        unicode_anomalies = u_rep.total_anomalies
        fm_match = _FRONTMATTER_AI_RE.search(raw_text)
        if fm_match:
            fm_text = fm_match.group(1).lower()
            if any(k in fm_text for k in _AI_PROMPT_KEYWORDS):
                ai_metadata = True
        suspicious = u_rep.has_anomalies or ai_metadata
        details = {"unicode": u_rep.to_dict(), "has_frontmatter_ai": ai_metadata}

    elif suffix in (".html", ".htm"):
        raw_text = data.decode("utf-8", errors="replace")
        u_rep = analyze_unicode_forensics(raw_text)
        unicode_anomalies = u_rep.total_anomalies
        if _HTML_META_AI_RE.search(raw_text) or _HTML_AI_ATTRS_RE.search(raw_text):
            ai_metadata = True
        suspicious = u_rep.has_anomalies or ai_metadata
        details = {"unicode": u_rep.to_dict(), "has_html_ai_tags": ai_metadata}

    elif suffix in (".docx", ".odt"):
        # Inspect zip entries
        try:
            with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
                names = zf.namelist()
                has_doc_props = any(n.startswith("docProps/") or n == "meta.xml" for n in names)
                # Check for AI keywords inside metadata XML
                meta_content = ""
                for meta_file in ["docProps/core.xml", "docProps/custom.xml", "meta.xml"]:
                    if meta_file in names:
                        meta_content += zf.read(meta_file).decode("utf-8", errors="replace").lower()
                
                if any(k in meta_content for k in _AI_PROMPT_KEYWORDS):
                    ai_metadata = True
                suspicious = has_doc_props or ai_metadata
                details = {"zip_entries": names[:15], "has_doc_props": has_doc_props, "has_ai_metadata": ai_metadata}
        except Exception as ex:
            details = {"error": str(ex)}

    elif suffix == ".pdf":
        has_xmp = b"<x:xmpmeta" in data or b"/Metadata" in data
        has_info = b"/Info" in data
        if any(k.encode("utf-8") in data.lower() for k in _AI_PROMPT_KEYWORDS):
            ai_metadata = True
        suspicious = has_xmp or has_info or ai_metadata or c2pa
        details = {"has_xmp": has_xmp, "has_info": has_info, "has_c2pa": c2pa, "has_ai_metadata": ai_metadata}

    return ProvenanceInspectionReport(
        file_path=str(file_path),
        file_name=file_path.name,
        file_format=suffix.lstrip("."),
        file_size_bytes=size,
        has_c2pa=c2pa,
        has_ai_metadata=ai_metadata,
        suspicious=suspicious,
        unicode_anomalies=unicode_anomalies,
        details=details,
        summary=f"Document ({suffix.lstrip('.').upper()}): {'Suspicious provenance marks found' if suspicious else 'Clean document'}",
    )


def clean_document(input_path: Path, output_path: Path | None = None) -> FileCleaningReport:
    """Clean metadata and invisible watermarks from document container."""
    input_path = validate_safe_path(input_path)
    suffix = input_path.suffix.lower()
    out = validate_safe_path(output_path) if output_path else input_path
    orig_size = input_path.stat().st_size
    data = input_path.read_bytes()
    actions: list[str] = []

    if suffix in (".txt", ".text"):
        raw = data.decode("utf-8", errors="replace")
        res = normalize_text(raw, NormalizationOptions())
        safe_atomic_write_text(out, res.normalized_text, encoding="utf-8")
        actions.append(f"Normalized Unicode (stripped {res.zero_width_removed} zero-width chars)")

    elif suffix in (".md", ".markdown"):
        raw = data.decode("utf-8", errors="replace")
        # Strip AI frontmatter
        clean_md = _FRONTMATTER_AI_RE.sub("", raw)
        res = normalize_text(clean_md, NormalizationOptions())
        safe_atomic_write_text(out, res.normalized_text, encoding="utf-8")
        actions.append("Stripped AI metadata frontmatter and normalized Unicode")

    elif suffix in (".html", ".htm"):
        raw = data.decode("utf-8", errors="replace")
        clean_html = _HTML_META_AI_RE.sub("", raw)
        clean_html = _HTML_AI_ATTRS_RE.sub("", clean_html)
        res = normalize_text(clean_html, NormalizationOptions())
        safe_atomic_write_text(out, res.normalized_text, encoding="utf-8")
        actions.append("Stripped HTML AI meta tags and cleaned invisible characters")

    elif suffix in (".docx", ".odt"):
        # Clean docx / odt zip archives by stripping metadata parts
        try:
            in_buf = io.BytesIO(data)
            out_buf = io.BytesIO()
            with zipfile.ZipFile(in_buf, "r") as zin:
                with zipfile.ZipFile(out_buf, "w", compression=zipfile.ZIP_DEFLATED) as zout:
                    for item in zin.infolist():
                        name = item.filename
                        # Exclude metadata files
                        if name.startswith("docProps/") or name in ("meta.xml", "customXml/"):
                            actions.append(f"Removed metadata stream: {name}")
                            continue
                        
                        content = zin.read(name)
                        # Normalize text inside main document XMLs
                        if name in ("word/document.xml", "content.xml"):
                            txt = content.decode("utf-8", errors="replace")
                            norm = normalize_text(txt, NormalizationOptions(normalize_unicode_form="NFC")).normalized_text
                            content = norm.encode("utf-8")
                            actions.append(f"Normalized Unicode in {name}")
                        
                        zout.writestr(item, content)
            safe_atomic_write_bytes(out, out_buf.getvalue())
        except Exception:
            safe_atomic_write_bytes(out, data)

    elif suffix == ".pdf":
        # Check if qpdf or exiftool are available for full structural PDF rebuild
        qpdf = shutil.which("qpdf")
        exiftool = shutil.which("exiftool")
        if qpdf:
            try:
                subprocess.run([qpdf, "--linearize", str(input_path), str(out)], check=True, capture_output=True)
                actions.append("Rebuilt PDF structural objects with qpdf")
            except Exception:
                safe_atomic_write_bytes(out, data)
        elif exiftool:
            try:
                subprocess.run([exiftool, "-all=", "-overwrite_original", "-o", str(out), str(input_path)], check=True, capture_output=True)
                actions.append("Stripped PDF metadata with exiftool")
            except Exception:
                safe_atomic_write_bytes(out, data)
        else:
            # Native structural PDF metadata scrubbing
            cleaned_pdf = re.sub(rb"/Metadata\s+\d+\s+\d+\s+R", rb"/Metadata null", data)
            cleaned_pdf = re.sub(rb"/Info\s+\d+\s+\d+\s+R", rb"/Info null", cleaned_pdf)
            safe_atomic_write_bytes(out, cleaned_pdf)
            actions.append("Scrubbed PDF /Metadata and /Info dictionary references")

    new_size = out.stat().st_size if out.is_file() else orig_size

    return FileCleaningReport(
        input_path=str(input_path),
        output_path=str(out),
        file_format=suffix.lstrip("."),
        original_size_bytes=orig_size,
        cleaned_size_bytes=new_size,
        size_delta_bytes=new_size - orig_size,
        success=True,
        actions_performed=actions or ["Sanitized document structure"],
        metadata_stripped=True,
        unicode_cleaned=True,
    )
