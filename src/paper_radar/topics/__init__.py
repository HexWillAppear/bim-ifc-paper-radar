"""Available paper-radar topics."""

from __future__ import annotations

from .base import TopicConfig
from .bim_ifc import TOPIC as BIM_IFC
from .hypergraph_rag import TOPIC as HYPERGRAPH_RAG
from .self_evolving_agent import TOPIC as SELF_EVOLVING_AGENT


TOPICS: dict[str, TopicConfig] = {
    topic.slug: topic
    for topic in (
        BIM_IFC,
        SELF_EVOLVING_AGENT,
        HYPERGRAPH_RAG,
    )
}
DEFAULT_TOPIC = BIM_IFC


def get_topic(slug: str) -> TopicConfig:
    """Return a topic by CLI slug."""

    try:
        return TOPICS[slug]
    except KeyError as exc:
        choices = ", ".join(TOPICS)
        raise ValueError(f"unknown topic {slug!r}; choose one of: {choices}") from exc


__all__ = [
    "BIM_IFC",
    "DEFAULT_TOPIC",
    "HYPERGRAPH_RAG",
    "SELF_EVOLVING_AGENT",
    "TOPICS",
    "TopicConfig",
    "get_topic",
]
