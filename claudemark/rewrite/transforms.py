"""Local syntactic transformations, synonym substitution, and cadence rebalancing."""

from __future__ import annotations

import random
import re
from typing import Any

# Curated synonym dictionary for safe local transformation without external models.
# Includes lemmas, inflections (-s, -ed, -ing), adjectives, adverbs, and connectors.
_SYNONYMS: dict[str, list[str]] = {
    # Transitions and connectors
    "furthermore": ["moreover", "in addition", "additionally", "besides"],
    "moreover": ["furthermore", "in addition", "additionally", "likewise"],
    "however": ["nevertheless", "yet", "still", "nonetheless", "conversely"],
    "nevertheless": ["nonetheless", "however", "still", "yet"],
    "nonetheless": ["nevertheless", "however", "still", "even so"],
    "therefore": ["consequently", "thus", "as a result", "hence", "accordingly"],
    "consequently": ["therefore", "as a result", "thus", "hence"],
    "thus": ["hence", "therefore", "consequently", "as such"],
    "hence": ["thus", "therefore", "as a result"],
    "additionally": ["furthermore", "moreover", "also", "in addition"],
    "subsequently": ["later", "afterward", "then", "thereafter", "following this"],
    "ultimately": ["eventually", "in the end", "finally", "at last"],
    "predominantly": ["primarily", "mostly", "largely", "chiefly"],
    "primarily": ["mainly", "mostly", "chiefly", "predominantly"],
    "notably": ["especially", "particularly", "markedly", "specifically"],
    "specifically": ["particularly", "expressly", "explicitly", "notably"],
    "conversely": ["on the other hand", "in contrast", "opposite to this"],
    "meanwhile": ["at the same time", "simultaneously", "concurrently"],
    "essentially": ["fundamentally", "basically", "at core", "in essence"],
    "inherently": ["naturally", "intrinsically", "by nature"],
    "comprehensively": ["thoroughly", "extensively", "completely"],
    "significantly": ["substantially", "notably", "considerably", "markedly"],

    # Common multi-word AI transition phrases
    "it is important to note that": ["notably", "importantly", "it is worth noting that", "significantly"],
    "it is worth noting that": ["notably", "importantly", "it should be noted that"],
    "in order to": ["to", "so as to"],
    "due to the fact that": ["because", "since", "as"],
    "at this point in time": ["currently", "now", "presently"],
    "plays a crucial role in": ["is central to", "is key to", "is essential for"],
    "plays a significant role in": ["is important to", "contributes to", "is vital for"],
    "take into consideration": ["consider", "account for", "evaluate"],
    "a wide range of": ["many", "various", "numerous", "a diverse set of"],
    "a variety of": ["various", "different", "multiple", "several"],
    "in conclusion": ["to summarize", "in summary", "overall", "to conclude"],
    "in terms of": ["regarding", "concerning", "with respect to"],
    "with respect to": ["concerning", "regarding", "as to"],
    "as a matter of fact": ["in fact", "actually", "indeed"],
    "shed light on": ["clarify", "illuminate", "explain"],

    # Verbs and their inflected forms
    "demonstrate": ["show", "illustrate", "exhibit", "indicate", "display"],
    "demonstrates": ["shows", "illustrates", "exhibits", "indicates", "displays"],
    "demonstrated": ["showed", "illustrated", "exhibited", "indicated"],
    "demonstrating": ["showing", "illustrating", "exhibiting", "indicating"],

    "utilize": ["use", "employ", "apply", "leverage"],
    "utilizes": ["uses", "employs", "applies", "leverages"],
    "utilized": ["used", "employed", "applied", "leveraged"],
    "utilizing": ["using", "employing", "applying", "leveraging"],

    "implement": ["execute", "apply", "carry out", "deploy"],
    "implements": ["executes", "applies", "carries out", "deploys"],
    "implemented": ["executed", "applied", "carried out", "deployed"],
    "implementing": ["executing", "applying", "carrying out", "deploying"],

    "facilitate": ["enable", "assist", "help", "streamline", "support"],
    "facilitates": ["enables", "assists", "helps", "streamlines", "supports"],
    "facilitated": ["enabled", "assisted", "helped", "streamlined"],
    "facilitating": ["enabling", "assisting", "helping", "streamlining"],

    "illustrate": ["demonstrate", "show", "clarify", "explain"],
    "illustrates": ["demonstrates", "shows", "clarifies", "explains"],
    "illustrated": ["demonstrated", "showed", "clarified", "explained"],
    "illustrating": ["demonstrating", "showing", "clarifying", "explaining"],

    "indicate": ["suggest", "show", "signal", "point to"],
    "indicates": ["suggests", "shows", "signals", "points to"],
    "indicated": ["suggested", "showed", "signaled"],
    "indicating": ["suggesting", "showing", "signaling"],

    "synthesize": ["combine", "integrate", "unify", "merge"],
    "synthesizes": ["combines", "integrates", "unifies", "merges"],
    "synthesized": ["combined", "integrated", "unified", "merged"],
    "synthesizing": ["combining", "integrating", "unifying", "merging"],

    "evaluate": ["assess", "examine", "appraise", "analyze"],
    "evaluates": ["assesses", "examines", "appraises", "analyzes"],
    "evaluated": ["assessed", "examined", "appraised", "analyzed"],
    "evaluating": ["assessing", "examining", "appraising", "analyzing"],

    "generate": ["produce", "create", "yield", "originate"],
    "generates": ["produces", "creates", "yields", "originates"],
    "generated": ["produced", "created", "yielded"],
    "generating": ["producing", "creating", "yielding"],

    "establish": ["set up", "build", "create", "formulate"],
    "establishes": ["sets up", "builds", "creates", "formulates"],
    "established": ["set up", "built", "created", "formed"],
    "establishing": ["setting up", "building", "creating", "forming"],

    "incorporate": ["include", "integrate", "embody", "adopt"],
    "incorporates": ["includes", "integrates", "embodies", "adopts"],
    "incorporated": ["included", "integrated", "embodied", "adopted"],
    "incorporating": ["including", "integrating", "embodying", "adopting"],

    # Adjectives
    "significant": ["substantial", "notable", "considerable", "meaningful", "important"],
    "crucial": ["essential", "vital", "critical", "pivotal", "key"],
    "essential": ["crucial", "vital", "fundamental", "necessary", "key"],
    "substantial": ["considerable", "significant", "large", "notable"],
    "comprehensive": ["thorough", "extensive", "complete", "in-depth", "detailed"],
    "sophisticated": ["advanced", "complex", "refined", "elaborate"],
    "intricate": ["complex", "detailed", "elaborate"],
    "nuanced": ["subtle", "refined", "detailed"],
    "paramount": ["vital", "critical", "supreme", "primary"],
    "pivotal": ["central", "crucial", "critical", "key"],
    "prominent": ["leading", "notable", "major", "salient"],
    "pertinent": ["relevant", "applicable", "appropriate"],
    "optimal": ["ideal", "best", "most favorable"],
    "robust": ["strong", "sturdy", "resilient", "reliable"],
    "diverse": ["varied", "different", "assorted"],
    "meaningful": ["significant", "valuable", "purposeful"],
    "approximately": ["roughly", "about", "around", "nearly"],
    "paradigm": ["framework", "model", "approach", "pattern"],
}


def substitute_synonyms(
    text: str,
    substitution_rate: float = 0.4,
    seed: int | None = 42,
) -> str:
    """Safely replace transition phrases and high-frequency watermark tokens.

    Preserves sentence capitalization, punctuation, and casing while ensuring
    substitutions occur deterministically when candidate words exist.
    """
    if not text or not text.strip():
        return text

    rng = random.Random(seed)
    result = text

    # Step 1: Process multi-word phrases first (longest phrases first)
    multi_phrases = sorted(
        [k for k in _SYNONYMS if " " in k],
        key=len,
        reverse=True,
    )
    for phrase in multi_phrases:
        if phrase in result.lower():
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            alts = _SYNONYMS[phrase]
            
            def _replace_phrase(match: re.Match[str]) -> str:
                matched_str = match.group(0)
                chosen = rng.choice(alts)
                if matched_str and matched_str[0].isupper():
                    chosen = chosen[0].upper() + chosen[1:]
                return chosen

            if rng.random() < max(substitution_rate, 0.5):
                result = pattern.sub(_replace_phrase, result, count=1)

    # Step 2: Identify candidate single-word tokens
    words = result.split()
    candidates = []
    for idx, w in enumerate(words):
        clean_w = w.strip(".,;:!?()\"'[]{}").lower()
        if clean_w in _SYNONYMS and " " not in clean_w:
            candidates.append((idx, w, clean_w))

    if not candidates:
        return result

    # Calculate substitutions to perform (at least 1 if substitution_rate > 0)
    target_count = max(1, int(round(len(candidates) * substitution_rate))) if substitution_rate > 0 else 0
    chosen_indices = set(rng.sample([c[0] for c in candidates], min(target_count, len(candidates))))

    transformed_words = []
    for idx, w in enumerate(words):
        if idx in chosen_indices:
            clean_w = w.strip(".,;:!?()\"'[]{}").lower()
            alts = _SYNONYMS.get(clean_w, [])
            if alts:
                chosen = rng.choice(alts)
                # Preserve leading punctuation
                leading_punct = ""
                for char in w:
                    if char in ".,;:!?()\"'[]{}":
                        leading_punct += char
                    else:
                        break
                # Preserve trailing punctuation
                trailing_punct = ""
                for char in reversed(w):
                    if char in ".,;:!?()\"'[]{}":
                        trailing_punct = char + trailing_punct
                    else:
                        break
                
                # Preserve uppercase / title casing
                if w and w[0].isupper():
                    chosen = chosen[0].upper() + chosen[1:]
                if w.isupper() and len(w) > 1:
                    chosen = chosen.upper()

                transformed_words.append(leading_punct + chosen + trailing_punct)
                continue

        transformed_words.append(w)

    return " ".join(transformed_words)


def rebalance_cadence(text: str) -> str:
    """Rebalance sentence length cadence to disrupt strict token burstiness constraints.

    Transforms overly uniform compound structures and clauses, diversifying n-gram
    transitions and entropy distributions without altering core semantics.
    """
    if not text or not text.strip():
        return text

    # Transform common compound clause markers
    mod_text = text

    # Simplify repetitive filler structures
    mod_text = re.sub(r',\s*which\s+(?:is|are|was|were)\s+', ', ', mod_text)
    mod_text = re.sub(r',\s*and\s+(?:thereby|thus|consequently)\s+', '; thus, ', mod_text)
    mod_text = re.sub(r',\s*in\s+order\s+to\s+', ' to ', mod_text)

    # Break overly long compound sentences joined by semicolons or connectors if long
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', mod_text) if s.strip()]
    if not sentences:
        return mod_text

    processed = []
    for s in sentences:
        # If sentence is very long (> 30 words) and has a conjunction, split for cadence variety
        words_in_s = s.split()
        if len(words_in_s) > 30 and ", and " in s:
            parts = s.split(", and ", 1)
            p1 = parts[0].strip() + "."
            p2 = parts[1].strip()
            if p2:
                p2 = p2[0].upper() + p2[1:]
            processed.append(p1 + " " + p2)
        else:
            processed.append(s)

    return " ".join(processed)

