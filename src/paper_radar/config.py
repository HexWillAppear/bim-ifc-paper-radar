"""Global defaults and backwards-compatible BIM/IFC configuration aliases."""

from __future__ import annotations

from .topics import DEFAULT_TOPIC
from .topics.bim_ifc import CONTEXT_TERMS


DEFAULT_USER_AGENT = (
    "research-paper-radar/0.2 "
    "(+https://github.com/HexWillAppear/bim-ifc-paper-radar)"
)

# Existing imports keep working while new code reads the selected TopicConfig.
OPENALEX_QUERIES = list(DEFAULT_TOPIC.openalex_queries)
ARXIV_QUERY_TERMS = list(DEFAULT_TOPIC.arxiv_query_terms)
PHRASE_WEIGHTS = DEFAULT_TOPIC.phrase_weights
MIN_RELEVANCE_SCORE = DEFAULT_TOPIC.min_relevance_score
DEFAULT_DAYS = 30
DEFAULT_MAX_PER_SOURCE = 80
