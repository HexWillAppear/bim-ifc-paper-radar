from __future__ import annotations

import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from paper_radar.collect import collect
from paper_radar.topics import SELF_EVOLVING_AGENT


class TopicCollectionTests(unittest.TestCase):
    def test_collect_writes_a_new_topic_to_its_own_directories(self) -> None:
        incoming = [
            {
                "source": "test",
                "source_id": "self-evolving-1",
                "title": "A self-evolving agent with adaptive memory",
                "abstract": "A language model agent improves itself from interaction.",
                "authors": ["A. Researcher"],
                "published": dt.date.today().isoformat(),
                "url": "https://example.test/self-evolving-1",
            }
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            with (
                patch("paper_radar.collect.fetch_all", return_value=(incoming, [])) as fetch_all,
                patch(
                    "paper_radar.collect.summarize_missing_papers",
                    return_value=(0, []),
                ) as summarize,
            ):
                result = collect(
                    days=30,
                    max_per_source=10,
                    data_dir=root / "data",
                    public_dir=root / "public",
                    summarize_limit=0,
                    topic=SELF_EVOLVING_AGENT,
                )

            data_path = root / "data" / "self-evolving-agent" / "papers.json"
            public_path = root / "public" / "self-evolving-agent" / "papers.json"
            payload = json.loads(data_path.read_text(encoding="utf-8"))

            self.assertTrue(data_path.exists())
            self.assertTrue(public_path.exists())
            self.assertEqual(payload["topic"]["slug"], "self-evolving-agent")
            self.assertEqual(payload["count"], 1)
            self.assertEqual(result["topic"], "self-evolving-agent")
            self.assertEqual(fetch_all.call_args.kwargs["topic"], SELF_EVOLVING_AGENT)
            self.assertEqual(summarize.call_args.kwargs["topic_title"], "自进化 Agent")


if __name__ == "__main__":
    unittest.main()
