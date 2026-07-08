"""Relevance scoring for BIM/IFC papers."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .config import CONTEXT_TERMS, MIN_RELEVANCE_SCORE, PHRASE_WEIGHTS


WORD_BIM = re.compile(r"\bbim\b", re.IGNORECASE)
WORD_IFC = re.compile(r"\bifc\b", re.IGNORECASE)


@dataclass(frozen=True)
class MatchResult:
    score: int
    matched_terms: list[str]
    relevant: bool


def normalize_text(value: str | None) -> str:
    """Lowercase text and collapse punctuation-heavy whitespace."""

    if not value:
        return ""
    normalized = unicodedata.normalize("NFKC", value).lower()
    normalized = normalized.replace("_", " ")
    normalized = re.sub(r"[^\w\s+-]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def has_context(text: str) -> bool:
    return any(term in text for term in CONTEXT_TERMS)


def score_text(title: str | None, abstract: str | None) -> MatchResult:
    title_text = normalize_text(title)
    body_text = normalize_text(abstract)
    combined = f"{title_text} {body_text}".strip()
    matched: dict[str, int] = {}
    score = 0

    for phrase, weight in PHRASE_WEIGHTS.items():
        if phrase in combined:
            title_boost = 2 if phrase in title_text else 0
            matched[phrase] = weight + title_boost
            score += weight + title_boost

    context = has_context(combined)

    if WORD_BIM.search(title_text) and context:
        matched.setdefault("BIM", 8)
        score += 8
    elif WORD_BIM.search(body_text) and context:
        matched.setdefault("BIM", 5)
        score += 5

    if WORD_IFC.search(title_text) and ("industry foundation" in combined or context or WORD_BIM.search(combined)):
        matched.setdefault("IFC", 8)
        score += 8
    elif WORD_IFC.search(body_text) and ("industry foundation" in combined or WORD_BIM.search(combined)):
        matched.setdefault("IFC", 5)
        score += 5

    ordered_terms = [
        term for term, _ in sorted(matched.items(), key=lambda item: (-item[1], item[0].lower()))
    ]
    return MatchResult(score=score, matched_terms=ordered_terms, relevant=score >= MIN_RELEVANCE_SCORE)

