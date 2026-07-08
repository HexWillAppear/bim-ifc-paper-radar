from __future__ import annotations

import unittest

from paper_radar.matching import score_text
from paper_radar.storage import merge_papers


class MatchingTests(unittest.TestCase):
    def test_clear_bim_title_is_relevant(self) -> None:
        result = score_text(
            "A BIM-based digital twin workflow for bridge construction",
            "The method integrates point cloud data and facility management.",
        )

        self.assertTrue(result.relevant)
        self.assertIn("BIM", result.matched_terms)

    def test_ifc_finance_context_is_not_relevant(self) -> None:
        result = score_text(
            "IFC investment patterns in emerging markets",
            "International finance case studies and risk analysis.",
        )

        self.assertFalse(result.relevant)

    def test_dedupe_prefers_doi(self) -> None:
        existing = [{"title": "Old", "doi": "https://doi.org/10.123/example", "score": 7}]
        incoming = [
            {
                "title": "New",
                "doi": "https://doi.org/10.123/example",
                "score": 12,
                "matched_terms": ["openbim"],
            }
        ]

        merged = merge_papers(existing, incoming)

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["title"], "New")
        self.assertEqual(merged[0]["score"], 12)

    def test_dedupe_merges_matching_titles_without_doi(self) -> None:
        existing = [{"title": "BIM and IFC coordination for hospitals", "source_id": "openalex-a", "score": 9}]
        incoming = [
            {
                "title": "BIM and IFC coordination for hospitals",
                "source_id": "openalex-b",
                "score": 11,
                "matched_terms": ["BIM", "IFC"],
            }
        ]

        merged = merge_papers(existing, incoming)

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["source_id"], "openalex-b")
        self.assertEqual(merged[0]["score"], 11)


if __name__ == "__main__":
    unittest.main()
