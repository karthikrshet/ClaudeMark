"""Unicode forensics and invisible anomaly detection for ClaudeMark."""

from __future__ import annotations

import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any

# Zero-width / invisible codepoints
ZERO_WIDTH_CHARS = {
    0x200B: "ZERO WIDTH SPACE (ZWSP)",
    0x200C: "ZERO WIDTH NON-JOINER (ZWNJ)",
    0x200D: "ZERO WIDTH JOINER (ZWJ)",
    0x2060: "WORD JOINER (WJ)",
    0xFEFF: "ZERO WIDTH NO-BREAK SPACE / BOM",
    0x2061: "FUNCTION APPLICATION",
    0x2062: "INVISIBLE TIMES",
    0x2063: "INVISIBLE SEPARATOR",
    0x2064: "INVISIBLE PLUS",
    0x180E: "MONGOLIAN VOWEL SEPARATOR",
}

# Special spaces and whitespace anomalies
SPECIAL_SPACES = {
    0x00A0: "NO-BREAK SPACE (NBSP)",
    0x2000: "EN QUAD",
    0x2001: "EM QUAD",
    0x2002: "EN SPACE",
    0x2003: "EM SPACE",
    0x2004: "THREE-PER-EM SPACE",
    0x2005: "FOUR-PER-EM SPACE",
    0x2006: "SIX-PER-EM SPACE",
    0x2007: "FIGURE SPACE",
    0x2008: "PUNCTUATION SPACE",
    0x2009: "THIN SPACE",
    0x200A: "HAIR SPACE",
    0x202F: "NARROW NO-BREAK SPACE",
    0x205F: "MEDIUM MATHEMATICAL SPACE",
    0x3000: "IDEOGRAPHIC SPACE",
}

# Bidirectional overrides & embeddings
BIDI_CONTROLS = {
    0x200E: "LEFT-TO-RIGHT MARK",
    0x200F: "RIGHT-TO-LEFT MARK",
    0x202A: "LEFT-TO-RIGHT EMBEDDING",
    0x202B: "RIGHT-TO-LEFT EMBEDDING",
    0x202C: "POP DIRECTIONAL FORMATTING",
    0x202D: "LEFT-TO-RIGHT OVERRIDE",
    0x202E: "RIGHT-TO-LEFT OVERRIDE",
    0x2066: "LEFT-TO-RIGHT ISOLATE",
    0x2067: "RIGHT-TO-LEFT ISOLATE",
    0x2068: "FIRST STRONG ISOLATE",
    0x2069: "POP DIRECTIONAL ISOLATE",
}

# Common mixed-script homoglyphs targeting Latin
HOMOGLYPH_CYRILLIC_LATIN = {
    'а': 'a', 'с': 'c', 'е': 'e', 'о': 'o', 'р': 'p', 'х': 'x', 'у': 'y',
    'А': 'A', 'В': 'B', 'С': 'C', 'Е': 'E', 'Н': 'H', 'І': 'I', 'Ј': 'J',
    'К': 'K', 'М': 'M', 'О': 'O', 'Р': 'P', 'Ѕ': 'S', 'Т': 'T', 'Х': 'X',
}


@dataclass
class AnomalyDetail:
    codepoint: str
    name: str
    count: int
    category: str
    sample_positions: list[int] = field(default_factory=list)


@dataclass
class UnicodeForensicReport:
    has_anomalies: bool = False
    total_anomalies: int = 0
    zero_width_count: int = 0
    nbsp_count: int = 0
    special_space_count: int = 0
    bidi_control_count: int = 0
    control_char_count: int = 0
    bom_present: bool = False
    homoglyph_count: int = 0
    
    # Normalization form analysis
    is_nfc: bool = True
    is_nfkc: bool = True
    is_nfd: bool = True
    is_nfkd: bool = True
    
    # Detailed findings breakdown
    findings: list[AnomalyDetail] = field(default_factory=list)
    summary_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def analyze_unicode_forensics(text: str) -> UnicodeForensicReport:
    """Perform forensic Unicode inspection on text to detect hidden watermarks,
    steganographic markers, and anomalies.
    """
    if not text:
        return UnicodeForensicReport()

    bom_present = text.startswith("\ufeff")
    
    # Normalization checks
    nfc = unicodedata.normalize("NFC", text)
    nfkc = unicodedata.normalize("NFKC", text)
    nfd = unicodedata.normalize("NFD", text)
    nfkd = unicodedata.normalize("NFKD", text)

    is_nfc = (text == nfc)
    is_nfkc = (text == nfkc)
    is_nfd = (text == nfd)
    is_nfkd = (text == nfkd)

    zero_width_map: dict[int, list[int]] = {}
    special_space_map: dict[int, list[int]] = {}
    bidi_map: dict[int, list[int]] = {}
    control_map: dict[int, list[int]] = {}
    homoglyph_map: dict[str, list[int]] = {}

    for idx, char in enumerate(text):
        cp = ord(char)
        
        # Zero-width chars
        if cp in ZERO_WIDTH_CHARS:
            zero_width_map.setdefault(cp, []).append(idx)
        # Special spaces
        elif cp in SPECIAL_SPACES:
            special_space_map.setdefault(cp, []).append(idx)
        # BiDi overrides
        elif cp in BIDI_CONTROLS:
            bidi_map.setdefault(cp, []).append(idx)
        # Control chars (C0 and C1 controls, except standard whitespace \t, \n, \r)
        elif unicodedata.category(char) in ("Cc", "Cf", "Co", "Cs"):
            if char not in ("\t", "\n", "\r"):
                control_map.setdefault(cp, []).append(idx)

    # Detect homoglyphs in primarily Latin words
    words = text.split()
    for word in words:
        has_latin = any('a' <= c.lower() <= 'z' for c in word)
        if has_latin:
            for c in word:
                if c in HOMOGLYPH_CYRILLIC_LATIN:
                    homoglyph_map.setdefault(c, []).append(text.find(c))

    findings: list[AnomalyDetail] = []
    
    # Aggregate zero-width findings
    zw_count = 0
    for cp, positions in zero_width_map.items():
        zw_count += len(positions)
        findings.append(AnomalyDetail(
            codepoint=f"U+{cp:04X}",
            name=ZERO_WIDTH_CHARS[cp],
            count=len(positions),
            category="zero_width",
            sample_positions=positions[:5],
        ))

    # Aggregate special spaces
    nbsp_count = len(special_space_map.get(0x00A0, []))
    spec_space_count = 0
    for cp, positions in special_space_map.items():
        spec_space_count += len(positions)
        findings.append(AnomalyDetail(
            codepoint=f"U+{cp:04X}",
            name=SPECIAL_SPACES[cp],
            count=len(positions),
            category="whitespace",
            sample_positions=positions[:5],
        ))

    # Aggregate bidi
    bidi_count = 0
    for cp, positions in bidi_map.items():
        bidi_count += len(positions)
        findings.append(AnomalyDetail(
            codepoint=f"U+{cp:04X}",
            name=BIDI_CONTROLS[cp],
            count=len(positions),
            category="bidi",
            sample_positions=positions[:5],
        ))

    # Aggregate control chars
    ctrl_count = 0
    for cp, positions in control_map.items():
        ctrl_count += len(positions)
        try:
            uname = unicodedata.name(chr(cp))
        except ValueError:
            uname = f"CONTROL_0x{cp:02X}"
        findings.append(AnomalyDetail(
            codepoint=f"U+{cp:04X}",
            name=uname,
            count=len(positions),
            category="control",
            sample_positions=positions[:5],
        ))

    # Aggregate homoglyphs
    homo_count = 0
    for char, positions in homoglyph_map.items():
        homo_count += len(positions)
        findings.append(AnomalyDetail(
            codepoint=f"U+{ord(char):04X}",
            name=f"HOMOGLYPH '{char}' (looks like Latin '{HOMOGLYPH_CYRILLIC_LATIN.get(char)}')",
            count=len(positions),
            category="homoglyph",
            sample_positions=positions[:5],
        ))

    total_anomalies = zw_count + spec_space_count + bidi_count + ctrl_count + homo_count
    has_anomalies = total_anomalies > 0 or not is_nfc or bom_present

    # Construct readable summary text
    summary_parts = []
    if zw_count > 0:
        summary_parts.append(f"{zw_count} zero-width character(s)")
    if nbsp_count > 0:
        summary_parts.append(f"{nbsp_count} NBSP character(s)")
    if (spec_space_count - nbsp_count) > 0:
        summary_parts.append(f"{spec_space_count - nbsp_count} non-standard space(s)")
    if bidi_count > 0:
        summary_parts.append(f"{bidi_count} BiDi override(s)")
    if ctrl_count > 0:
        summary_parts.append(f"{ctrl_count} hidden control character(s)")
    if homo_count > 0:
        summary_parts.append(f"{homo_count} mixed-script homoglyph(s)")
    if bom_present:
        summary_parts.append("BOM header detected")
    if not is_nfc:
        summary_parts.append("non-NFC normalization")

    summary_text = ", ".join(summary_parts) if summary_parts else "Clean (No Unicode anomalies detected)"

    return UnicodeForensicReport(
        has_anomalies=has_anomalies,
        total_anomalies=total_anomalies,
        zero_width_count=zw_count,
        nbsp_count=nbsp_count,
        special_space_count=spec_space_count,
        bidi_control_count=bidi_count,
        control_char_count=ctrl_count,
        bom_present=bom_present,
        homoglyph_count=homo_count,
        is_nfc=is_nfc,
        is_nfkc=is_nfkc,
        is_nfd=is_nfd,
        is_nfkd=is_nfkd,
        findings=findings,
        summary_text=summary_text,
    )


def visualize_unicode_markers(text: str) -> str:
    """Make invisible Unicode markers, directional overrides, and unusual whitespace visible."""
    if not text:
        return ""

    out = []
    for ch in text:
        cp = ord(ch)
        if cp == 0x200B:
            out.append("<ZWSP>")
        elif cp == 0x200C:
            out.append("<ZWNJ>")
        elif cp == 0x200D:
            out.append("<ZWJ>")
        elif cp == 0x2060:
            out.append("<WJ>")
        elif cp == 0xFEFF:
            out.append("<BOM>")
        elif cp == 0x00A0:
            out.append("<NBSP>")
        elif cp == 0x202F:
            out.append("<NNBSP>")
        elif cp == 0x00AD:
            out.append("<SHY>")
        elif cp == 0x180E:
            out.append("<MVS>")
        elif 0x2000 <= cp <= 0x200A:
            out.append(f"<SPACE-U+{cp:04X}>")
        elif cp in BIDI_CONTROLS:
            short_bidi = {
                0x200E: "LRM", 0x200F: "RLM", 0x202A: "LRE", 0x202B: "RLE",
                0x202C: "PDF", 0x202D: "LRO", 0x202E: "RLO", 0x2066: "LRI",
                0x2067: "RLI", 0x2068: "FSI", 0x2069: "PDI",
            }.get(cp, f"BIDI-U+{cp:04X}")
            out.append(f"<{short_bidi}>")
        elif 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF:
            out.append(f"<VS-{cp:X}>")
        elif 0xE0000 <= cp <= 0xE007F:
            out.append(f"<TAG-{cp:X}>")
        elif unicodedata.category(ch).startswith("C") and ch not in ("\n", "\r", "\t"):
            out.append(f"<CTRL-U+{cp:04X}>")
        else:
            out.append(ch)

    return "".join(out)
