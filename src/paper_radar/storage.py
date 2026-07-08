"""Read, merge, and write collected paper data."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def load_papers(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return list(payload.get("papers", []))
    if isinstance(payload, list):
        return payload
    return []


def write_json(path: Path, papers: list[dict[str, Any]], days: int, warnings: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "query_window_days": days,
        "count": len(papers),
        "warnings": warnings or [],
        "papers": papers,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, papers: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "title",
        "published",
        "source",
        "venue",
        "doi",
        "url",
        "pdf_url",
        "score",
        "matched_terms",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for paper in papers:
            writer.writerow(
                {
                    field: "; ".join(paper.get(field, []))
                    if isinstance(paper.get(field), list)
                    else paper.get(field, "")
                    for field in fields
                }
            )


def merge_papers(existing: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    key_index: dict[str, str] = {}
    record_counter = 0
    now = dt.datetime.now(dt.timezone.utc).isoformat()

    def add_record(paper: dict[str, Any], seen_now: bool) -> None:
        nonlocal record_counter
        keys = paper_keys(paper)
        matches: list[str] = []
        for key in keys:
            primary = key_index.get(key)
            if primary and primary not in matches:
                matches.append(primary)

        if matches:
            primary = matches[0]
            for duplicate in matches[1:]:
                if duplicate == primary or duplicate not in merged:
                    continue
                merged[primary] = _merge_existing(merged[primary], merged.pop(duplicate), now=now)
                for index_key, index_primary in list(key_index.items()):
                    if index_primary == duplicate:
                        key_index[index_key] = primary

            if seen_now:
                previous = merged.get(primary, {})
                first_seen = previous.get("first_seen") or now
                merged[primary] = _merge_one(previous, paper, first_seen=first_seen, last_seen=now)
            else:
                merged[primary] = _merge_existing(merged.get(primary, {}), paper, now=now)
        else:
            primary = keys[0] if keys else f"record:{record_counter}"
            record_counter += 1
            merged[primary] = dict(paper)

        for key in paper_keys(merged[primary]):
            key_index[key] = primary

    for paper in existing:
        add_record(paper, seen_now=False)

    for paper in incoming:
        add_record(paper, seen_now=True)

    return sorted(
        merged.values(),
        key=lambda paper: (paper.get("published") or "", paper.get("score") or 0),
        reverse=True,
    )


def paper_key(paper: dict[str, Any]) -> str:
    keys = paper_keys(paper)
    return keys[0] if keys else "unknown"


def paper_keys(paper: dict[str, Any]) -> list[str]:
    keys: list[str] = []

    doi = _clean_identifier(paper.get("doi"))
    if doi:
        keys.append(f"doi:{doi}")

    title = title_fingerprint(str(paper.get("title") or ""))
    if title:
        keys.append(f"title:{title}")

    url = _clean_identifier(paper.get("url"))
    if url:
        keys.append(f"url:{url}")

    source_id = _clean_identifier(paper.get("source_id"))
    if source_id:
        keys.append(f"source:{source_id}")

    return keys


def title_fingerprint(title: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
    if not cleaned:
        return ""
    return hashlib.sha1(cleaned.encode("utf-8")).hexdigest()


def _clean_identifier(value: Any) -> str:
    if not value:
        return ""
    return str(value).strip().lower().rstrip("/")


def _merge_one(
    previous: dict[str, Any], paper: dict[str, Any], first_seen: str, last_seen: str
) -> dict[str, Any]:
    merged = dict(previous)
    for key, value in paper.items():
        if value not in (None, "", [], {}):
            merged[key] = value
    previous_terms = set(previous.get("matched_terms", []))
    new_terms = set(paper.get("matched_terms", []))
    merged["matched_terms"] = sorted(previous_terms | new_terms, key=str.lower)
    merged["score"] = max(int(previous.get("score") or 0), int(paper.get("score") or 0))
    merged["first_seen"] = first_seen
    merged["last_seen"] = last_seen
    return merged


def _merge_existing(previous: dict[str, Any], paper: dict[str, Any], now: str) -> dict[str, Any]:
    first_seen = previous.get("first_seen") or paper.get("first_seen") or now
    last_seen = max(
        [value for value in [previous.get("last_seen"), paper.get("last_seen")] if value],
        default=now,
    )
    return _merge_one(previous, paper, first_seen=first_seen, last_seen=last_seen)
