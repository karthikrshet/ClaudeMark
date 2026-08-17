"""Cryptographic Forensic Audit Certificate Generator for ClaudeMark.

Generates standalone, verifiable, print-ready HTML and JSON audit certificates.
Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

import datetime
import hashlib
from pathlib import Path
from typing import Any


def generate_html_certificate(
    target_name: str,
    target_bytes: bytes,
    report_data: dict[str, Any],
    certificate_id: str | None = None,
) -> str:
    """Generate self-contained, verifiable HTML audit certificate."""
    sha256_hash = hashlib.sha256(target_bytes).hexdigest()
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    cert_id = certificate_id or f"CM-{sha256_hash[:12].upper()}"

    is_clean = not report_data.get("suspicious", False)
    if "watermark_result" in report_data:
        wm = report_data.get("watermark_result", {})
        if isinstance(wm, dict) and wm.get("is_watermarked"):
            is_clean = False

    status_badge = "VERIFIED CLEAN" if is_clean else "SUSPICIOUS MARKS DETECTED"
    status_color = "#10B981" if is_clean else "#EF4444"
    status_bg = "#064E3B" if is_clean else "#7F1D1D"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ClaudeMark Forensic Certificate - {cert_id}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #060911;
      color: #F8FAFC;
      margin: 0;
      padding: 40px 20px;
      display: flex;
      justify-content: center;
    }}
    .cert-card {{
      background-color: #0E1626;
      border: 1px solid #1C2A44;
      border-radius: 16px;
      max-width: 800px;
      width: 100%;
      padding: 40px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #1C2A44;
      padding-bottom: 24px;
      margin-bottom: 28px;
    }}
    .brand {{
      font-size: 24px;
      font-weight: 800;
      color: #FFFFFF;
    }}
    .brand span {{ color: #06B6D4; }}
    .badge {{
      background-color: {status_bg};
      color: {status_color};
      border: 1px solid {status_color};
      font-size: 12px;
      font-weight: 800;
      padding: 6px 16px;
      border-radius: 9999px;
      letter-spacing: 0.5px;
    }}
    .section {{
      margin-bottom: 24px;
    }}
    .label {{
      font-size: 12px;
      color: #64748B;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }}
    .value {{
      font-size: 15px;
      color: #F8FAFC;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      word-break: break-all;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-top: 20px;
    }}
    .grid-box {{
      background-color: #162036;
      border: 1px solid #1C2A44;
      border-radius: 8px;
      padding: 16px;
    }}
    .footer {{
      border-top: 1px solid #1C2A44;
      padding-top: 20px;
      margin-top: 32px;
      font-size: 12px;
      color: #64748B;
      display: flex;
      justify-content: space-between;
    }}
  </style>
</head>
<body>
  <div class="cert-card">
    <div class="header">
      <div>
        <div class="brand">Claude<span>Mark</span> Forensics</div>
        <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">Certificate of Cryptographic & Forensic Audit</div>
      </div>
      <div class="badge">{status_badge}</div>
    </div>

    <div class="section">
      <div class="label">Target Resource</div>
      <div class="value">{target_name}</div>
    </div>

    <div class="section">
      <div class="label">SHA-256 Content Digest</div>
      <div class="value">{sha256_hash}</div>
    </div>

    <div class="grid">
      <div class="grid-box">
        <div class="label">Audit Certificate ID</div>
        <div class="value">{cert_id}</div>
      </div>
      <div class="grid-box">
        <div class="label">Timestamp</div>
        <div class="value">{timestamp}</div>
      </div>
    </div>

    <div class="grid">
      <div class="grid-box">
        <div class="label">Zero-Width Steganography</div>
        <div class="value" style="color: {'#10B981' if is_clean else '#EF4444'};">
          {report_data.get('total_unicode_anomalies', 0)} Anomalies Detected
        </div>
      </div>
      <div class="grid-box">
        <div class="label">Container Provenance (C2PA/EXIF)</div>
        <div class="value" style="color: {'#10B981' if is_clean else '#EF4444'};">
          {report_data.get('total_c2pa_manifests', 0)} Tracking Manifests
        </div>
      </div>
    </div>

    <div class="footer">
      <div>Engine: ClaudeMark v2.0.0 (Zero-Egress Host Execution)</div>
      <div>https://github.com/karthikrshet/ClaudeMark</div>
    </div>
  </div>
</body>
</html>"""
    return html


def save_audit_certificate(
    target_path: Path,
    report_data: dict[str, Any],
    output_cert_path: Path,
) -> Path:
    """Write HTML audit certificate to destination file."""
    data_bytes = target_path.read_bytes() if target_path.is_file() else str(report_data).encode("utf-8")
    html_cert = generate_html_certificate(target_path.name, data_bytes, report_data)
    output_cert_path.parent.mkdir(parents=True, exist_ok=True)
    output_cert_path.write_text(html_cert, encoding="utf-8")
    return output_cert_path
