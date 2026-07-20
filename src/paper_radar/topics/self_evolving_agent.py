"""Self-evolving agent topic definition."""

from __future__ import annotations

from .base import CooccurrenceRule, TopicConfig


AGENT_CONTEXT = (
    "agent",
    "agents",
    "agentic",
    "language model",
    "llm",
    "multi-agent",
    "multi agent",
    "autonomous system",
)


TOPIC = TopicConfig(
    slug="self-evolving-agent",
    title="Self-Evolving Agents",
    description="自进化、自改进与持续学习的 AI/LLM Agent 相关工作。",
    summary_context="自进化 Agent",
    openalex_queries=(
        '"self-evolving agent"',
        '"self evolving agent"',
        '"self-evolving agents"',
        '"self-improving agent"',
        '"self improving agent"',
        '"agent self-evolution"',
        '"agent self evolution"',
        '"evolving language agents"',
        '"continually improving agents"',
    ),
    arxiv_query_terms=(
        'all:"self-evolving agent"',
        'all:"self evolving agent"',
        'all:"self-improving agent"',
        'all:"self improving agent"',
        'all:"agent self-evolution"',
        'all:"agent self evolution"',
        'all:"evolving language agents"',
        'all:"continually improving agents"',
    ),
    phrase_weights={
        "self-evolving agent": 12,
        "self-evolving agents": 12,
        "self evolving agent": 12,
        "self evolving agents": 12,
        "self-improving agent": 11,
        "self-improving agents": 11,
        "self improving agent": 11,
        "self improving agents": 11,
        "agent self-evolution": 12,
        "agent self evolution": 12,
        "evolving language agent": 10,
        "evolving language agents": 10,
        "continually improving agent": 9,
        "continually improving agents": 9,
        "recursive self-improvement": 7,
        "lifelong agent": 7,
        "lifelong agents": 7,
    },
    cooccurrence_rules=(
        CooccurrenceRule(
            label="self-evolution + agent",
            groups=(
                (
                    "self-evolution",
                    "self evolution",
                    "self-evolving",
                    "self evolving",
                    "self-improvement",
                    "self improvement",
                    "self-improving",
                    "self improving",
                ),
                AGENT_CONTEXT,
            ),
            weight=8,
            title_boost=2,
        ),
    ),
    output_subdir="self-evolving-agent",
)
