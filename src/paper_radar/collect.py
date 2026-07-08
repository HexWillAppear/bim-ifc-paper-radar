"""Command-line collector for daily BIM/IFC papers."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Any

from .config import DEFAULT_DAYS, DEFAULT_MAX_PER_SOURCE
from .matching import score_text
from .sources import fetch_all
from .storage import load_papers, merge_papers, write_csv, write_json


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def collect(days: int, max_per_source: int, data_dir: Path, public_dir: Path) -> dict[str, Any]:
    since = dt.date.today() - dt.timedelta(days=days)
    incoming, warnings = fetch_all(since=since, max_per_source=max_per_source)
    relevant = []

    for paper in incoming:
        result = score_text(paper.get("title"), paper.get("abstract"))
        if result.relevant:
            normalized = dict(paper)
            normalized["score"] = result.score
            normalized["matched_terms"] = result.matched_terms
            relevant.append(normalized)

    data_path = data_dir / "papers.json"
    csv_path = data_dir / "papers.csv"
    public_path = public_dir / "papers.json"
    existing = load_papers(data_path)
    merged = [paper for paper in merge_papers(existing, relevant) if not _is_future_paper(paper)]

    write_json(data_path, merged, days=days, warnings=warnings)
    write_json(public_path, merged, days=days, warnings=warnings)
    write_csv(csv_path, merged)

    return {
        "incoming": len(incoming),
        "relevant": len(relevant),
        "total": len(merged),
        "warnings": warnings,
        "data_path": str(data_path),
        "public_path": str(public_path),
    }


def _is_future_paper(paper: dict[str, Any]) -> bool:
    value = str(paper.get("published") or "")
    try:
        published = dt.date.fromisoformat(value[:10])
    except ValueError:
        return False
    return published > dt.date.today()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect BIM/IFC papers and update static data files.")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Rolling publication-date window.")
    parser.add_argument(
        "--max-per-source",
        type=int,
        default=DEFAULT_MAX_PER_SOURCE,
        help="Maximum records requested from each source/query.",
    )
    parser.add_argument("--data-dir", type=Path, default=PROJECT_ROOT / "data")
    parser.add_argument("--public-dir", type=Path, default=PROJECT_ROOT / "public")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = collect(days=args.days, max_per_source=args.max_per_source, data_dir=args.data_dir, public_dir=args.public_dir)
    print(
        "Collected {incoming} candidates, kept {relevant} relevant papers, "
        "{total} total records.".format(**summary)
    )
    if summary["warnings"]:
        print("Completed with source warnings:")
        for warning in summary["warnings"]:
            print(f"- {warning}")
    print(f"Data: {summary['data_path']}")
    print(f"Public JSON: {summary['public_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
