# Rule: Zero-Width Unicode & Manuscript Hygiene

When generating, editing, or inspecting markdown, documentation, copy, or source code in this workspace:

1. **Zero-Width Character Prohibition**: Never inject zero-width spaces (`U+200B`), zero-width joiners (`U+200D`), word joiners (`U+2060`), byte-order marks (`U+FEFF`), or BiDi directional overrides into user-facing prose.
2. **ASCII Whitespace Normalization**: Standardize whitespace to standard ASCII spaces (`U+0020`) and newline characters (`\n`). Avoid non-breaking spaces (`U+00A0`) in ordinary documentation unless syntactically necessary.
3. **Forensic Verification**: When requested to audit files or verify hygiene, invoke ClaudeMark via `python claudemark.py unicode inspect <file>` or `python claudemark.py audit .`.
