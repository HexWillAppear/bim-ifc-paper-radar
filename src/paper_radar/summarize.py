"""Optional Chinese AI summaries through OpenAI-compatible model APIs."""

from __future__ import annotations

import datetime as dt
import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEEPSEEK_CHAT_URL = "https://api.deepseek.com/chat/completions"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_SUMMARY_MODEL = "gpt-5.5"
DEFAULT_SUMMARY_LIMIT = 20


class SummaryError(RuntimeError):
    """The summarizer failed, but collection can continue."""


def default_summary_limit() -> int:
    value = os.getenv("AI_SUMMARY_LIMIT", "").strip()
    if not value:
        return DEFAULT_SUMMARY_LIMIT
    try:
        return max(0, int(value))
    except ValueError:
        return DEFAULT_SUMMARY_LIMIT


def summarize_missing_papers(
    papers: list[dict[str, Any]],
    limit: int | None = None,
    refresh: bool = False,
) -> tuple[int, list[str]]:
    summarizer = build_summarizer()
    if summarizer is None:
        return 0, []

    remaining = default_summary_limit() if limit is None else max(0, limit)
    warnings: list[str] = []
    updated = 0

    for paper in papers:
        if remaining <= 0:
            break
        if paper.get("ai_summary_zh") and not refresh:
            continue
        if not paper.get("title"):
            continue

        try:
            paper["ai_summary_zh"] = summarizer.summarize_paper(paper)
            paper["ai_summary_model"] = summarizer.model
            paper["ai_summary_updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
            updated += 1
            remaining -= 1
        except SummaryError as exc:
            warnings.append(f"AI summary failed for {paper.get('title', 'untitled')}: {exc}")
            break

        time.sleep(0.5)

    return updated, warnings


def build_summarizer() -> "DeepSeekSummarizer | OpenAISummarizer | None":
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if deepseek_key:
        return DeepSeekSummarizer(api_key=deepseek_key)

    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if openai_key:
        return OpenAISummarizer(api_key=openai_key)

    return None


class DeepSeekSummarizer:
    def __init__(self, api_key: str, model: str | None = None) -> None:
        self.api_key = api_key
        self.model = (
            model
            or os.getenv("DEEPSEEK_MODEL", "").strip()
            or os.getenv("AI_SUMMARY_MODEL", "").strip()
            or DEFAULT_DEEPSEEK_MODEL
        )

    def summarize_paper(self, paper: dict[str, Any]) -> str:
        prompt = build_summary_prompt(paper)
        payload = {
            "model": self.model,
            "thinking": {"type": "disabled"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是BIM/IFC论文情报助理。请只用简体中文输出摘要，"
                        "不要编造论文中没有的信息。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 220,
            "stream": False,
        }
        response = _post_json(DEEPSEEK_CHAT_URL, payload, self.api_key)
        summary = extract_chat_completion_text(response).strip()
        if not summary:
            raise SummaryError("empty model output")
        return " ".join(summary.split())


class OpenAISummarizer:
    def __init__(self, api_key: str, model: str | None = None) -> None:
        self.api_key = api_key
        self.model = model or os.getenv("OPENAI_MODEL", "").strip() or DEFAULT_SUMMARY_MODEL

    def summarize_paper(self, paper: dict[str, Any]) -> str:
        prompt = build_summary_prompt(paper)
        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "developer",
                    "content": (
                        "你是BIM/IFC论文情报助理。请只用简体中文输出摘要，"
                        "不要编造论文中没有的信息。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_output_tokens": 220,
            "store": False,
        }
        response = _post_json(OPENAI_RESPONSES_URL, payload, self.api_key)
        summary = extract_output_text(response).strip()
        if not summary:
            raise SummaryError("empty model output")
        return " ".join(summary.split())


def build_summary_prompt(paper: dict[str, Any]) -> str:
    authors = ", ".join((paper.get("authors") or [])[:6])
    abstract = str(paper.get("abstract") or "").strip()
    if len(abstract) > 1800:
        abstract = abstract[:1800] + "..."
    if not abstract:
        abstract = "暂无英文摘要；请仅根据标题、来源和关键词做保守概括，不要补充未给出的实验结果或结论。"

    return "\n".join(
        [
            "请为下面这篇BIM/IFC相关论文写中文AI摘要。",
            "要求：1-2句话，80-140个汉字；说明研究对象、方法或贡献；不输出项目符号；不要说“本文”。",
            "",
            f"标题：{paper.get('title') or ''}",
            f"作者：{authors}",
            f"来源：{paper.get('venue') or paper.get('source') or ''}",
            f"关键词命中：{', '.join(paper.get('matched_terms') or [])}",
            f"英文摘要：{abstract}",
        ]
    )


def extract_output_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]

    chunks: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    return "\n".join(chunks)


def extract_chat_completion_text(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content
    return ""


def _post_json(url: str, payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return json.loads(response.read().decode(charset, errors="replace"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise SummaryError(f"HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise SummaryError(str(exc)) from exc
