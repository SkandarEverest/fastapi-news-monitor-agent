import json
import hashlib
import os
from typing import Any

from app.utils.openai_client import get_openai_client
from app.utils.tavily_client import get_tavily_client
from .prompt import PLANNER_PROMPT, ARTICLE_SUMMARY_PROMPT, DIGEST_PROMPT

from urllib.parse import urlparse
from datetime import datetime, timezone

def _dedup_key(url: str, title: str) -> str:
    raw = (url.strip() + "|" + title.strip()).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return "Unknown"

def plan_queries(topic: str, keywords: list[str], window_hours: int) -> list[str]:
    client = get_openai_client()
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "Return only valid JSON. No markdown."},
            {"role": "user", "content": PLANNER_PROMPT.format(topic=topic, keywords=keywords, window_hours=window_hours)},
        ],
    )
    content = resp.choices[0].message.content or "[]"
    return json.loads(content)

def tavily_search(query: str) -> dict[str, Any]:
    tavily = get_tavily_client()
    return tavily.search(
        query=query,
        search_depth="advanced",
        include_raw_content="markdown",
    )

def extract_articles(search_payload: dict[str, Any]) -> list[dict[str, Any]]:
    results = search_payload.get("results") or []
    articles: list[dict[str, Any]] = []
    for r in results:
        content = (r.get("content") or "")
        raw_content = (r.get("raw_content") or "")

        text = content if content else raw_content
        text = text[:6000]

        articles.append(
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "published_date": r.get("published_date"),
                "score": r.get("score"),
                "text": text,
            }
        )
    return articles

def deduplicate_articles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for a in articles:
        url = (a.get("url") or "").strip()
        title = (a.get("title") or "").strip()
        if not url and not title:
            continue
        k = _dedup_key(url, title)
        if k in seen:
            continue
        seen.add(k)
        out.append(a)
    return out

def summarize_article(article: dict[str, Any]) -> str:
    client = get_openai_client()

    payload = {
        "title": article.get("title"),
        "url": article.get("url"),
        "published_date": article.get("published_date"),
        "text": article.get("text"),
    }

    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "Be concise. Use bullet points only."},
            {"role": "user", "content": ARTICLE_SUMMARY_PROMPT.format(article_json=json.dumps(payload))},
        ],
        max_tokens=250,
    )
    return resp.choices[0].message.content or ""

def synthesize_digest(topic: str, window_hours: int, summaries: list[dict[str, Any]]) -> str:
    client = get_openai_client()
    generated_at_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "Follow the format strictly. Output markdown only."},
            {"role": "user", "content": DIGEST_PROMPT.format(
                topic=topic,
                window_hours=window_hours,
                generated_at_utc=generated_at_utc,
                summaries=json.dumps(summaries),
            )},
        ],
    )
    return resp.choices[0].message.content or ""