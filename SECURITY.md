# Security Policy for ClaudeMark

ClaudeMark is designed from the ground up for analyzing and sanitizing untrusted, adversarial, and third-party files. This document details our security architecture, defensive mitigations, and responsible disclosure procedures.

---

## Supported Versions

| Version | Supported | Security Maintenance |
| :--- | :--- | :--- |
| `2.0.x` | Yes | Active security patches and vulnerability audits |
| `1.0.x` | Yes | Critical security patches only |
| `< 1.0` | No | End of life |

---

## Threat Model & Defensive Mitigations

Because ClaudeMark routinely ingests potentially untrusted files (PDFs, DOCX, ZIPs, images, and raw text), it implements defensive controls across six specific threat vectors:

### 1. Malicious PDF Actions & Embedded Exploits
* **Mitigation**: The PDF parser (`claudemark/security/scanner.py` and `claudemark/provenance/documents.py`) passively audits the structural object stream for dangerous PDF interactive elements:
  * `/JavaScript` and `/JS` execution blocks.
  * `/Launch` executable launch triggers.
  * `/EmbeddedFiles` payload attachments.
  * `/SubmitForm` and `/ImportData` remote exfiltration streams.
* Dangerous actions are flagged before sanitization, and structural linearization drops unreferenced exploit objects.

### 2. Decompression Bomb & Resource Exhaustion (Zip Bombs)
* **Mitigation**: DOCX, ODT, and archive containers are subjected to strict pre-decompression budgets:
  * Maximum compression ratio cap: **$100\times$**.
  * Uncompressed payload size ceiling: **100 MB**.
  * Total archive member count limit: **10,000 files**.
  * Files violating these thresholds are aborted immediately before in-memory expansion.

### 3. Malformed & Polyglot Images
* **Mitigation**: Image parsers (PNG, JPEG, WebP, SVG, AVIF, HEIC) parse structural chunk/segment/box headers using fixed-length bounds checking without executing image rendering decoders or spawning external shell viewers.

### 4. Path Traversal & Filename Sanitization
* **Mitigation**: All file paths supplied via CLI or REST API are validated with `validate_safe_path()`:
  * Normalized with `os.path.normpath` and `Path.resolve()`.
  * Checked for null-byte injections (`\0`).
  * Blocked from directory traversal escapes (`../`).
  * Windows reserved device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`) are strictly rejected.

### 5. Symlink Redirection & Race Conditions
* **Mitigation**: All write operations execute via `safe_atomic_write_bytes()` and `safe_atomic_write_text()`:
  * Content is written to a private temporary file (`.cm_tmp_*`) in the destination directory.
  * Existing symlink destinations are dereferenced and validated or rejected.
  * Atomic replacement is performed via `os.replace()`, eliminating partial write corruption and race conditions.

### 6. SSRF & Network Egress Boundaries
* **Mitigation**: The core engine operates under a strict **Zero-Egress** guarantee. Offline operations never establish outbound sockets. If website auditing is executed, local loopback binds and internal private IP ranges (RFC 1918 / RFC 4193) are blocked to prevent Server-Side Request Forgery (SSRF).

---

## Reporting a Vulnerability

We welcome responsible security reports from researchers and the open-source community.

If you discover a vulnerability in ClaudeMark:
1. **Private Reporting**: Submit an advisory via [GitHub Security Advisories](https://github.com/karthikrshet/ClaudeMark/security/advisories/new) or email [karthikrshet@users.noreply.github.com](mailto:karthikrshet@users.noreply.github.com).
2. **Details to Include**:
   * Vulnerability description and potential impact.
   * Proof of Concept (PoC) or minimal reproduction sample.
   * Affected version(s) and operating system.
3. **Response Timeline**:
   * **Initial Acknowledgment**: Within 24–48 hours.
   * **Triage & Validation**: Within 5 business days.
   * **Patch & Coordinated Disclosure**: Released promptly following fix verification.
