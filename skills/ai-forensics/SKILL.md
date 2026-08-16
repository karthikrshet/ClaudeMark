---
name: ai-forensics
description: Local-first AI watermark detection, Unicode steganography forensics, document sanitization, and C2PA provenance extraction.
---

# AI Forensics & Watermark Analysis Skill

Use this skill to inspect, analyze, disrupt, and sanitize AI watermarks and provenance metadata from text, documents, and images on content the user owns or is authorized to process.

## Available Actions

### 1. Statistical Watermark Analysis
Analyze text for subtle generative sampling biases and statistical regularities:
```bash
python claudemark.py analyze "<text>" --algorithm claude
```

### 2. Unicode & Steganography Inspection
Inspect and visualize hidden zero-width characters (`<ZWSP>`, `<BOM>`, `<RLO>`):
```bash
python claudemark.py unicode inspect file.txt
python claudemark.py unicode visualize file.txt
python claudemark.py unicode clean file.txt -o clean.txt
```

### 3. Best-Effort Statistical Watermark Disruption
Restructure cadence and rotate high-frequency transition tokens:
```bash
python claudemark.py rewrite file.txt -o rewritten.txt --strategy synonym_cadence
python claudemark.py evaluate file.txt rewritten.txt
```

### 4. File Provenance & Document Cleaning
Scrub metadata from 10 document and image formats (PDF, DOCX, ODT, HTML, MD, TXT, PNG, JPEG, WebP, SVG):
```bash
python claudemark.py inspect document.pdf
python claudemark.py clean document.pdf -o clean.pdf
```

### 5. Defensive Security Scanner
Scan files for zip bombs, malicious PDF actions, macros, and path traversal:
```bash
python claudemark.py security scan upload.pdf
```

## REST API Integration
If the server is running on `http://127.0.0.1:8765`:
- Analyze Text: `POST /api/analyze` `{"text": "..."}`
- Inspect Unicode: `POST /api/unicode/analyze` `{"text": "..."}`
- Clean File: `POST /clean` `{"file": "<base64>", "name": "doc.pdf"}`
- Agent Tool Dispatch: `POST /api/agent/exec` `{"tool_name": "...", "arguments": {...}}`
