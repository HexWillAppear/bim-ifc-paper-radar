from __future__ import annotations

import unittest

from paper_radar.matching import score_text
from paper_radar.storage import merge_papers
from paper_radar.summarize import build_summary_prompt, extract_chat_completion_text, extract_output_text
from paper_radar.topics import HYPERGRAPH_RAG, SELF_EVOLVING_AGENT, TOPICS


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

    def test_self_evolving_agent_phrase_is_relevant(self) -> None:
        result = score_text(
            "A self-evolving agent with lifelong tool-use memory",
            "The language model agent improves its policy from experience.",
            topic=SELF_EVOLVING_AGENT,
        )

        self.assertTrue(result.relevant)
        self.assertIn("self-evolving agent", result.matched_terms)

    def test_self_evolving_biology_without_agent_context_is_not_relevant(self) -> None:
        result = score_text(
            "Self-evolving protein networks in cellular biology",
            "We study mutation and selection in living cells.",
            topic=SELF_EVOLVING_AGENT,
        )

        self.assertFalse(result.relevant)

    def test_hypergraph_rag_cooccurrence_is_relevant(self) -> None:
        result = score_text(
            "Hypergraph indexing for knowledge-intensive generation",
            "Our retrieval-augmented generation pipeline traverses hypergraph relations.",
            topic=HYPERGRAPH_RAG,
        )

        self.assertTrue(result.relevant)
        self.assertIn("hypergraph + RAG", result.matched_terms)

    def test_plain_hypergraph_work_is_not_rag(self) -> None:
        result = score_text(
            "Hypergraph neural networks for recommendation",
            "A message-passing model for collaborative filtering.",
            topic=HYPERGRAPH_RAG,
        )

        self.assertFalse(result.relevant)

    def test_new_topics_have_independent_output_directories(self) -> None:
        self.assertEqual(TOPICS["self-evolving-agent"].output_subdir, "self-evolving-agent")
        self.assertEqual(TOPICS["hypergraph-rag"].output_subdir, "hypergraph-rag")

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

    def test_summary_prompt_requires_chinese(self) -> None:
        prompt = build_summary_prompt({"title": "IFC schema mapping", "abstract": "A mapping method."})

        self.assertIn("中文AI摘要", prompt)
        self.assertIn("80-140个汉字", prompt)

    def test_extract_output_text(self) -> None:
        payload = {
            "output": [
                {
                    "content": [
                        {"type": "output_text", "text": "这是中文摘要。"},
                    ]
                }
            ]
        }

        self.assertEqual(extract_output_text(payload), "这是中文摘要。")

    def test_extract_chat_completion_text(self) -> None:
        payload = {"choices": [{"message": {"content": "这是DeepSeek中文摘要。"}}]}

        self.assertEqual(extract_chat_completion_text(payload), "这是DeepSeek中文摘要。")


if __name__ == "__main__":
    unittest.main()
