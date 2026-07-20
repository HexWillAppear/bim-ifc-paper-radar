"""Configurable relevance scoring for every paper-radar topic."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .topics import DEFAULT_TOPIC
from .topics.base import TopicConfig
from .topics.bim_ifc import CONTEXT_TERMS


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


def _contains_term(text: str, term: str) -> bool:
    """Match a normalized term without accepting it inside a longer word."""

    normalized_term = normalize_text(term)
    if not normalized_term:
        return False
    return re.search(rf"(?<!\w){re.escape(normalized_term)}(?!\w)", text) is not None


def has_context(text: str) -> bool:
    """Retained for callers that use the original BIM/IFC context check."""

    return any(_contains_term(text, term) for term in CONTEXT_TERMS)


def score_text(
    title: str | None,
    abstract: str | None,
    topic: TopicConfig = DEFAULT_TOPIC,
) -> MatchResult:
    title_text = normalize_text(title)
    body_text = normalize_text(abstract)
    combined = f"{title_text} {body_text}".strip()
    matched: dict[str, int] = {}
    score = 0

    for phrase, weight in topic.phrase_weights.items():
        if _contains_term(combined, phrase):
            title_boost = 2 if _contains_term(title_text, phrase) else 0
            matched[phrase] = weight + title_boost
            score += weight + title_boost

    for rule in topic.cooccurrence_rules:
        if not all(any(_contains_term(combined, term) for term in group) for group in rule.groups):
            continue
        first_group_in_title = any(_contains_term(title_text, term) for term in rule.groups[0])
        rule_score = rule.weight + (rule.title_boost if first_group_in_title else 0)
        if rule.label not in matched:
            matched[rule.label] = rule_score
            score += rule_score

    ordered_terms = [
        term for term, _ in sorted(matched.items(), key=lambda item: (-item[1], item[0].lower()))
    ]
    return MatchResult(
        score=score,
        matched_terms=ordered_terms,
        relevant=score >= topic.min_relevance_score,
    )
