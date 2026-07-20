"""BIM/IFC topic definition."""

from __future__ import annotations

from .base import CooccurrenceRule, TopicConfig


CONTEXT_TERMS = (
    "aec",
    "architecture",
    "architectural",
    "asset management",
    "as-built",
    "bridge",
    "building",
    "built environment",
    "civil engineering",
    "construction",
    "digital twin",
    "facility",
    "facility management",
    "infrastructure",
    "laser scanning",
    "point cloud",
    "prefabrication",
    "quantity takeoff",
    "revit",
    "scan-to-bim",
    "structural",
    "urban",
)


TOPIC = TopicConfig(
    slug="bim-ifc",
    title="BIM/IFC",
    description=(
        "Building Information Modeling、IFC、openBIM 与 "
        "Industry Foundation Classes 相关论文。"
    ),
    summary_context="BIM/IFC",
    openalex_queries=(
        '"building information modeling"',
        '"building information modelling"',
        '"building information model"',
        '"industry foundation classes"',
        '"industry foundation class"',
        "openBIM",
        '"IFC schema"',
        '"IFC model"',
        '"IFC building"',
        '"BIM construction"',
        '"BIM digital twin"',
        '"scan-to-BIM"',
    ),
    arxiv_query_terms=(
        'all:"building information modeling"',
        'all:"building information modelling"',
        'all:"industry foundation classes"',
        "all:openBIM",
        'all:"IFC schema"',
        'all:"IFC model"',
        'all:"BIM construction"',
        'all:"BIM digital twin"',
        'all:"scan-to-BIM"',
    ),
    phrase_weights={
        "building information modeling": 12,
        "building information modelling": 12,
        "building information model": 10,
        "industry foundation classes": 12,
        "industry foundation class": 10,
        "openbim": 10,
        "ifc schema": 9,
        "ifc model": 8,
        "ifc models": 8,
        "ifc-based": 8,
        "ifc file": 7,
        "ifc files": 7,
        "scan-to-bim": 8,
        "scan to bim": 8,
        "bim-based": 7,
        "bim model": 7,
        "bim models": 7,
        "bim and ifc": 10,
        "digital twin": 3,
        "building energy model": 3,
    },
    cooccurrence_rules=(
        CooccurrenceRule(
            label="BIM",
            groups=(("bim",), CONTEXT_TERMS),
            weight=5,
            title_boost=3,
        ),
        CooccurrenceRule(
            label="IFC",
            groups=(
                ("ifc",),
                ("industry foundation", "bim", "openbim", *CONTEXT_TERMS),
            ),
            weight=5,
            title_boost=3,
        ),
    ),
    # Keep the original paths for backwards compatibility.
    output_subdir="",
)
