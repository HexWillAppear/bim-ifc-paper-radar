"""Search and relevance configuration for the paper radar."""

from __future__ import annotations

DEFAULT_USER_AGENT = "bim-ifc-paper-radar/0.1 (+https://github.com/)"

OPENALEX_QUERIES = [
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
]

ARXIV_QUERY_TERMS = [
    'all:"building information modeling"',
    'all:"building information modelling"',
    'all:"industry foundation classes"',
    "all:openBIM",
    'all:"IFC schema"',
    'all:"IFC model"',
    'all:"BIM construction"',
    'all:"BIM digital twin"',
    'all:"scan-to-BIM"',
]

PHRASE_WEIGHTS = {
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
}

CONTEXT_TERMS = {
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
}

MIN_RELEVANCE_SCORE = 7
DEFAULT_DAYS = 30
DEFAULT_MAX_PER_SOURCE = 80

