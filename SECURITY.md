# Security Policy for ClaudeMark

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reporting a Vulnerability

If you discover a potential security vulnerability in ClaudeMark, please report it responsibly by contacting the maintainer via GitHub Security Advisories or by emailing [karthikrshet@users.noreply.github.com](mailto:karthikrshet@users.noreply.github.com).

Please include:
1. Description of the vulnerability and attack vector.
2. Proof of Concept (PoC) file or reproduction script.
3. Affected versions and environment.

We aim to acknowledge reports within 48 hours and provide patches promptly.

---

## Defensive Architecture

ClaudeMark employs defensive engineering practices:
- **Zero Network Egress**: Core analysis and forensic tools never communicate over the internet.
- **Decompression Bomb Protection**: Zip containers are inspected with strict compression ratio limits ($100\times$) and uncompressed size ceilings ($100\text{ MB}$).
- **Path Traversal Guards**: Filenames and paths are normalized, null-byte inspected, and resolved within isolated temporary sandboxes.
- **Malicious Payload Disarming**: PDFs with embedded `/JavaScript`, `/Launch`, or `/EmbeddedFiles` and Office documents containing macros (`vbaProject.bin`) are flagged by the security scanner and never executed.
