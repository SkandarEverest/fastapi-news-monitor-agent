import os
import json
from datetime import datetime
from markdown import markdown
from weasyprint import HTML

from app.celery_app import celery_app
from .methods import (
    domain,
    plan_queries,
    tavily_search,
    extract_articles,
    deduplicate_articles,
    summarize_article,
    synthesize_digest,
)

OUTPUT_DIR = "outputs"


def run_monitoring(payload: dict) -> dict:
    # =========================
    # Step 1 — Validate & normalize input (already validated by Pydantic in FastAPI,
    # but we still safely normalize defaults in the worker)
    # =========================
    topic: str = payload["topic"]
    keywords: list[str] = payload.get("keywords") or []
    window_hours: int = int(payload.get("window_hours") or 24)
    max_articles: int = int(payload.get("max_articles") or 12)

    # Create output directory for generated files (JSON/MD/PDF)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # =========================
    # Step 2 — Planning step (LLM): create search queries
    # Agent decides "how to search" for the topic + keywords + time window
    # =========================
    queries = plan_queries(topic, keywords, window_hours)

    # =========================
    # Step 3 — Tool step (Tavily): search the web for each query
    # Collect raw search results (title/url/content/etc.)
    # =========================
    all_articles = []
    for q in queries:
        # Add a simple recency hint to bias results toward recent content
        q2 = f"{q} last {window_hours} hours"

        # Call Tavily search API
        search_payload = tavily_search(q2)

        # Extract relevant fields from Tavily response into a normalized article list
        all_articles.extend(extract_articles(search_payload))

    # =========================
    # Step 4 — Clean-up step: deduplicate + filter + cap results
    # Prevent duplicates across overlapping queries and limit total workload
    # =========================
    uniq = deduplicate_articles(all_articles)[:max_articles]

    # =========================
    # Step 5 — Reasoning step (LLM): summarize each article
    # Turn raw web results into short bullet summaries with key facts + references
    # =========================
    summarized = []
    for a in uniq:
        summary = summarize_article(a)
        summarized.append({
            "title": a.get("title"),
            "url": a.get("url"),
            "published_date": a.get("published_date"),
            "source": domain(a.get("url") or ""),
            "summary": summary,
        })

    # =========================
    # Step 6 — Synthesis step (LLM): create the final monitoring digest
    # Combine all summaries into:
    # - Executive summary
    # - Themes
    # - Alerts
    # - References
    # =========================
    digest_md = synthesize_digest(topic, window_hours, summarized)

    # =========================
    # Step 7 — Output step: export artifacts (JSON + Markdown + PDF)
    # Save the machine-readable + human-readable outputs
    # =========================
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    base = f"digest-{ts}"
    json_path = os.path.join(OUTPUT_DIR, f"{base}.json")
    md_path = os.path.join(OUTPUT_DIR, f"{base}.md")
    pdf_path = os.path.join(OUTPUT_DIR, f"{base}.pdf")

    # Save structured result for downstream usage
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {"topic": topic, "summaries": summarized, "digest_md": digest_md},
            f,
            ensure_ascii=False,
            indent=2,
        )

    # Save markdown digest for easy reading/editing
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(digest_md)

    # Convert markdown -> HTML -> PDF for a polished deliverable
    html = markdown(digest_md, output_format="html")
    HTML(string=html).write_pdf(pdf_path)

    # Return paths so API can show where artifacts were written
    return {
        "topic": topic,
        "queries": queries,
        "articles_count": len(uniq),
        "json_path": json_path,
        "md_path": md_path,
        "pdf_path": pdf_path,
    }


@celery_app.task(name="monitor_news_task")
def monitor_news_task(payload: dict):
    # Celery entrypoint: run the agentic workflow in background
    return run_monitoring(payload)