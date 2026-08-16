"""Safe text normalizer for ClaudeMark, removing hidden watermarks while preserving visible text."""

from __future__ import annotations

import unicodedata
from dataclasses import asdict, dataclass
from typing import Any

from .unicode_forensics import (
    BIDI_CONTROLS,
    HOMOGLYPH_CYRILLIC_LATIN,
    SPECIAL_SPACES,
    ZERO_WIDTH_CHARS,
)


@dataclass
class NormalizationOptions:
    strip_zero_width: bool = True
    normalize_spaces: bool = True
    strip_bidi_controls: bool = True
    strip_unprintable_controls: bool = True
    normalize_unicode_form: str = "NFC"  # 'NFC', 'NFKC', 'NFD', 'NFKD', or 'none'
    replace_homoglyphs: bool = False
    strip_bom: bool = True


@dataclass
class NormalizationResult:
    original_length: int
    normalized_length: int
    characters_removed: int
    characters_replaced: int
    zero_width_removed: int
    spaces_normalized: int
    bidi_removed: int
    controls_removed: int
    homoglyphs_replaced: int
    bom_removed: bool
    normalized_text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_text(
    text: str,
    options: NormalizationOptions | None = None,
) -> NormalizationResult:
    """Safely normalize text to eliminate invisible watermarks and encoding anomalies
    without corrupting ordinary readable prose, code, or symbols.
    """
    if options is None:
        options = NormalizationOptions()

    if not text:
        return NormalizationResult(
            original_length=0,
            normalized_length=0,
            characters_removed=0,
            characters_replaced=0,
            zero_width_removed=0,
            spaces_normalized=0,
            bidi_removed=0,
            controls_removed=0,
            homoglyphs_replaced=0,
            bom_removed=False,
            normalized_text="",
        )

    orig_len = len(text)
    cur_text = text
    bom_removed = False
    
    # 1. Strip BOM if present
    if options.strip_bom and cur_text.startswith("\ufeff"):
        cur_text = cur_text[1:]
        bom_removed = True

    zw_removed = 0
    spaces_norm = 0
    bidi_removed = 0
    ctrls_removed = 0
    homo_replaced = 0
    
    out_chars: list[str] = []
    
    for char in cur_text:
        cp = ord(char)
        
        # Zero-width removal
        if options.strip_zero_width and cp in ZERO_WIDTH_CHARS:
            zw_removed += 1
            if cp == 0xFEFF:
                bom_removed = True
            continue
            
        # BiDi control removal
        if options.strip_bidi_controls and cp in BIDI_CONTROLS:
            bidi_removed += 1
            continue
            
        # Unprintable control characters (Cc, Cf, etc. except \t, \n, \r)
        if options.strip_unprintable_controls and unicodedata.category(char) in ("Cc", "Cf", "Cs"):
            if char not in ("\t", "\n", "\r"):
                ctrls_removed += 1
                continue
                
        # Whitespace normalization
        if options.normalize_spaces and cp in SPECIAL_SPACES:
            out_chars.append(" ")
            spaces_norm += 1
            continue
            
        # Homoglyphs replacement
        if options.replace_homoglyphs and char in HOMOGLYPH_CYRILLIC_LATIN:
            out_chars.append(HOMOGLYPH_CYRILLIC_LATIN[char])
            homo_replaced += 1
            continue

        out_chars.append(char)

    processed_text = "".join(out_chars)

    # Unicode canonical normalization form
    if options.normalize_unicode_form and options.normalize_unicode_form.upper() != "NONE":
        norm_form = options.normalize_unicode_form.upper()
        if norm_form in ("NFC", "NFKC", "NFD", "NFKD"):
            processed_text = unicodedata.normalize(norm_form, processed_text)

    new_len = len(processed_text)
    chars_removed = (orig_len - new_len) if orig_len >= new_len else 0
    chars_replaced = spaces_norm + homo_replaced

    return NormalizationResult(
        original_length=orig_len,
        normalized_length=new_len,
        characters_removed=chars_removed,
        characters_replaced=chars_replaced,
        zero_width_removed=zw_removed,
        spaces_normalized=spaces_norm,
        bidi_removed=bidi_removed,
        controls_removed=ctrls_removed,
        homoglyphs_replaced=homo_replaced,
        bom_removed=bom_removed,
        normalized_text=processed_text,
    )
