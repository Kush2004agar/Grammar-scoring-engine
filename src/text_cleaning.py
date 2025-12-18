"""
Clean up spoken language text.

When people speak, they say things like "um", "uh", and repeat words.
This module removes that stuff so we can focus on the actual grammar.

Important: We DON'T fix grammar mistakes! If someone says "he go" instead
of "he goes", we keep it as "he go" because that's what they actually said,
and we want to score their actual grammar, not what we think they meant.

Design principles:
- Minimal: Only remove obvious noise (fillers, stutters)
- Conservative: When in doubt, keep the original
- Reproducible: Same input always gives same output
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


NON_LEXICAL_FILLERS = {"uh", "um", "erm", "eh", "uhm"}


@dataclass
class CleaningStats:
    """Counts of edits applied during cleaning."""

    num_tokens_raw: int = 0
    num_tokens_clean: int = 0
    fillers_removed: int = 0
    repetitions_collapsed: int = 0
    false_starts_trimmed: int = 0


def _normalise_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _lowercase(text: str) -> str:
    # We keep a lowercased version for modelling; the raw transcript
    # should be stored separately for audit.
    return text.lower()


def _remove_non_lexical_fillers(tokens: List[str], stats: CleaningStats) -> List[str]:
    cleaned: List[str] = []
    for tok in tokens:
        if tok in NON_LEXICAL_FILLERS:
            stats.fillers_removed += 1
            continue
        cleaned.append(tok)
    return cleaned


def _collapse_stutter_repetitions(tokens: List[str], stats: CleaningStats) -> List[str]:
    """Collapse immediate exact repetitions such as 'i i i' -> 'i'.

    Rationale: these repetitions are performance artefacts (stuttering)
    rather than intentional grammatical structures.
    """

    if not tokens:
        return tokens

    cleaned: List[str] = [tokens[0]]
    for tok in tokens[1:]:
        if tok == cleaned[-1]:
            stats.repetitions_collapsed += 1
            continue
        cleaned.append(tok)
    return cleaned


def _trim_simple_false_starts(tokens: List[str], stats: CleaningStats) -> List[str]:
    """Trim very short false starts immediately followed by a longer clause.

    Heuristic: if the first token is repeated as the second token sequence
    begins (e.g. ``[\"i\", \"i\", \"worked\", ...]``) we drop the first token.
    This is deliberately conservative to avoid removing meaningful content.
    """

    if len(tokens) >= 2 and tokens[0] == tokens[1]:
        stats.false_starts_trimmed += 1
        return tokens[1:]
    return tokens


def clean_transcript(text: str) -> tuple[str, CleaningStats]:
    """Clean an ASR transcript according to spoken-language rules.

    Parameters
    ----------
    text:
        Raw transcript string from ASR.

    Returns
    -------
    cleaned_text, stats
        ``cleaned_text`` is suitable for downstream grammar feature
        extraction; ``stats`` summarises the edits applied.
    """

    stats = CleaningStats()
    if not text:
        return "", stats

    # 1) Normalise whitespace and lowercase (for modelling only).
    normalized = _normalise_whitespace(text)
    lowered = _lowercase(normalized)

    # 2) Token-level operations.
    tokens = lowered.split(" ")
    stats.num_tokens_raw = len(tokens)

    tokens = _remove_non_lexical_fillers(tokens, stats)
    tokens = _trim_simple_false_starts(tokens, stats)
    tokens = _collapse_stutter_repetitions(tokens, stats)

    stats.num_tokens_clean = len(tokens)

    cleaned_text = " ".join(tokens)
    cleaned_text = _normalise_whitespace(cleaned_text)
    return cleaned_text, stats


