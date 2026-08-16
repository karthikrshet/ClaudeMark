---
name: ai-forensics
description: Local AI watermark detection, Unicode steganography visualization, container provenance stripping, and defensive file auditing with zero network egress.
---

# AI Forensics & Watermark Purifier (Antigravity IDE Skill)

Use this skill when you need to inspect or sanitize text, manuscripts, code, documents, or multimedia for AI watermarks, invisible Unicode steganography, C2PA Content Credentials, or hidden metadata.

## Core Workflows

### 1. Statistical AI Watermark Analysis
Analyze text for statistical token bias and entropy regularity:
```bash
python claudemark.py analyze manuscript.txt --algorithm claude --verbose
```

### 2. Unicode Steganography Forensics & Visualization
Inspect and expose hidden zero-width spaces, joiners, tags, and directional overrides:
```bash
python claudemark.py unicode visualize manuscript.txt
python claudemark.py unicode clean manuscript.txt -o clean.txt
```

### 3. Container Provenance & Metadata Sanitization
Strip C2PA manifests, EXIF, XMP, and generator tags from documents, images, and multimedia:
```bash
python claudemark.py inspect document.pdf
python claudemark.py clean document.pdf -o clean.pdf
python claudemark.py clean image.png -o clean.png
```

### 4. Recursive Workspace Audit
Audit the whole repository for watermarks and security threats:
```bash
python claudemark.py audit .
```

### 5. Interactive Side-by-Side Forensic Diff
```bash
python claudemark.py diff original.txt clean.txt --html -o diff_report.html
```
