"""Hypergraph RAG topic definition."""

from __future__ import annotations

from .base import CooccurrenceRule, TopicConfig


TOPIC = TopicConfig(
    slug="hypergraph-rag",
    title="Hypergraph RAG",
    description="使用超图进行知识组织、检索或推理的 RAG 相关工作。",
    summary_context="超图 RAG",
    openalex_queries=(
        '"hypergraph RAG"',
        '"hypergraph retrieval augmented generation"',
        '"hypergraph retrieval-augmented generation"',
        '"hypergraph-based RAG"',
        '"hypergraph based retrieval augmented generation"',
        '"HyperGraphRAG"',
    ),
    arxiv_query_terms=(
        'all:"hypergraph RAG"',
        'all:"hypergraph retrieval augmented generation"',
        'all:"hypergraph retrieval-augmented generation"',
        'all:"hypergraph-based RAG"',
        'all:"HyperGraphRAG"',
    ),
    phrase_weights={
        "hypergraph rag": 12,
        "hypergraphrag": 12,
        "hypergraph-rag": 12,
        "hypergraph retrieval augmented generation": 12,
        "hypergraph retrieval-augmented generation": 12,
        "hypergraph-based rag": 11,
        "hypergraph based rag": 11,
        "hypergraph-based retrieval": 9,
        "hypergraph based retrieval": 9,
    },
    cooccurrence_rules=(
        CooccurrenceRule(
            label="hypergraph + RAG",
            groups=(
                ("hypergraph", "hyper-graph"),
                (
                    "rag",
                    "retrieval augmented generation",
                    "retrieval-augmented generation",
                    "retrieval augmented language model",
                ),
            ),
            weight=8,
            title_boost=2,
        ),
    ),
    output_subdir="hypergraph-rag",
)
