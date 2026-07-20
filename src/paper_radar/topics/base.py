"""Shared topic configuration types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CooccurrenceRule:
    """Add a relevance score when every term group is represented in the text."""

    label: str
    groups: tuple[tuple[str, ...], ...]
    weight: int
    title_boost: int = 0


@dataclass(frozen=True)
class TopicConfig:
    """Queries, matching rules, and presentation metadata for one radar topic."""

    slug: str
    title: str
    description: str
    summary_context: str
    openalex_queries: tuple[str, ...]
    arxiv_query_terms: tuple[str, ...]
    phrase_weights: dict[str, int]
    cooccurrence_rules: tuple[CooccurrenceRule, ...] = ()
    min_relevance_score: int = 7
    output_subdir: str = ""
