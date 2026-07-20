"""Source adapters for OpenAlex and arXiv."""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import DEFAULT_USER_AGENT
from .topics import DEFAULT_TOPIC
from .topics.base import TopicConfig


OPENALEX_WORKS_URL = "https://api.openalex.org/works"
ARXIV_QUERY_URL = "https://export.arxiv.org/api/query"


class SourceError(RuntimeError):
    """A source failed while the collector can continue with other sources."""


def _get_text(url: str, params: dict[str, Any], accept: str) -> str:
    query = urlencode(params)
    request = Request(
        f"{url}?{query}",
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": accept,
        },
    )
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read().decode(charset, errors="replace")
        except HTTPError as exc:
            if exc.code in {429, 500, 502, 503, 504} and attempt < 2:
                retry_after = exc.headers.get("Retry-After")
                wait_seconds = int(retry_after) if retry_after and retry_after.isdigit() else 10 * (attempt + 1)
                time.sleep(wait_seconds)
                continue
            raise SourceError(f"HTTP {exc.code}: {exc.reason}") from exc
        except (URLError, TimeoutError) as exc:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            raise SourceError(str(exc)) from exc
    raise SourceError("request failed after retries")


def _date_or_none(value: str | None) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value[:10])
    except ValueError:
        return None


def _reconstruct_openalex_abstract(index: dict[str, list[int]] | None) -> str:
    if not index:
        return ""
    words: list[tuple[int, str]] = []
    for word, positions in index.items():
        for position in positions:
            words.append((position, word))
    return " ".join(word for _, word in sorted(words))


def _openalex_mailto() -> str | None:
    value = os.getenv("OPENALEX_MAILTO", "").strip()
    return value or None


def fetch_openalex(
    since: dt.date,
    max_per_query: int,
    topic: TopicConfig = DEFAULT_TOPIC,
) -> list[dict[str, Any]]:
    papers: list[dict[str, Any]] = []
    mailto = _openalex_mailto()
    today = dt.date.today()

    for query in topic.openalex_queries:
        params: dict[str, Any] = {
            "search": query,
            "filter": f"from_publication_date:{since.isoformat()},to_publication_date:{today.isoformat()}",
            "per-page": min(max_per_query, 200),
            "sort": "publication_date:desc",
        }
        if mailto:
            params["mailto"] = mailto

        try:
            payload = json.loads(_get_text(OPENALEX_WORKS_URL, params, accept="application/json"))
        except (json.JSONDecodeError, SourceError) as exc:
            raise SourceError(f"OpenAlex request failed for {query}: {exc}") from exc

        for item in payload.get("results", []):
            papers.append(_normalize_openalex_work(item))

    return papers


def _normalize_openalex_work(item: dict[str, Any]) -> dict[str, Any]:
    primary_location = item.get("primary_location") or {}
    source = primary_location.get("source") or {}
    open_access = item.get("open_access") or {}
    authors = [
        authorship.get("author", {}).get("display_name")
        for authorship in item.get("authorships", [])
        if authorship.get("author", {}).get("display_name")
    ]
    doi = item.get("doi")
    url = doi or item.get("id") or primary_location.get("landing_page_url")

    return {
        "source": "OpenAlex",
        "source_id": item.get("id"),
        "title": item.get("display_name") or "",
        "abstract": _reconstruct_openalex_abstract(item.get("abstract_inverted_index")),
        "authors": authors,
        "published": item.get("publication_date") or item.get("publication_year"),
        "updated": item.get("updated_date"),
        "doi": doi,
        "url": url,
        "pdf_url": primary_location.get("pdf_url") or open_access.get("oa_url"),
        "venue": source.get("display_name") or "",
    }


def fetch_arxiv(
    since: dt.date,
    max_results: int,
    topic: TopicConfig = DEFAULT_TOPIC,
) -> list[dict[str, Any]]:
    query = " OR ".join(topic.arxiv_query_terms)
    params = {
        "search_query": query,
        "start": 0,
        "max_results": min(max_results, 300),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    xml_text = _get_text(ARXIV_QUERY_URL, params, accept="application/atom+xml")
    today = dt.date.today()
    return [
        paper
        for paper in _parse_arxiv_feed(xml_text)
        if (published := _date_or_none(paper.get("published"))) is None or since <= published <= today
    ]


def _parse_arxiv_feed(xml_text: str) -> list[dict[str, Any]]:
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise SourceError(f"arXiv returned invalid XML: {exc}") from exc

    papers: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns):
        entry_id = _text(entry.find("atom:id", ns))
        title = " ".join(_text(entry.find("atom:title", ns)).split())
        abstract = " ".join(_text(entry.find("atom:summary", ns)).split())
        authors = [_text(author.find("atom:name", ns)) for author in entry.findall("atom:author", ns)]
        pdf_url = ""
        page_url = entry_id
        for link in entry.findall("atom:link", ns):
            href = link.attrib.get("href", "")
            if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                pdf_url = href
            elif link.attrib.get("rel") == "alternate":
                page_url = href
        doi = _text(entry.find("arxiv:doi", ns))
        primary_category = entry.find("arxiv:primary_category", ns)
        category = primary_category.attrib.get("term", "") if primary_category is not None else ""

        papers.append(
            {
                "source": "arXiv",
                "source_id": entry_id,
                "title": title,
                "abstract": abstract,
                "authors": [author for author in authors if author],
                "published": _text(entry.find("atom:published", ns)),
                "updated": _text(entry.find("atom:updated", ns)),
                "doi": doi,
                "url": page_url,
                "pdf_url": pdf_url,
                "venue": category,
            }
        )

    return papers


def _text(element: ET.Element[str] | None) -> str:
    return (element.text or "").strip() if element is not None else ""


def fetch_all(
    since: dt.date,
    max_per_source: int,
    topic: TopicConfig = DEFAULT_TOPIC,
) -> tuple[list[dict[str, Any]], list[str]]:
    sources: list[tuple[str, Any]] = [
        ("OpenAlex", fetch_openalex),
        ("arXiv", fetch_arxiv),
    ]
    papers: list[dict[str, Any]] = []
    warnings: list[str] = []

    for name, fetcher in sources:
        try:
            papers.extend(fetcher(since, max_per_source, topic))
        except SourceError as exc:
            message = f"{name}: {exc}"
            warnings.append(message)
            print(f"warning: {message}", file=sys.stderr)
        time.sleep(1)

    return papers, warnings
