PLANNER_PROMPT = """Return EXACTLY a valid JSON array of 6 search queries (string values).
Do not include markdown, explanations, or any extra keys.

Goal: monitor breaking/recent news about the topic within the time window.

Rules:
- Each query should be different (cover different angles).
- Include recency cues like: "latest", "today", "this week", "breaking", "update".
- Prefer high-signal sources when relevant (e.g., Reuters, AP, FT, WSJ, BBC, The Verge, TechCrunch, official blogs).
- Keep each query <= 12 words.

Topic: {topic}
Keywords: {keywords}
WindowHours: {window_hours}
"""


ARTICLE_SUMMARY_PROMPT = """You are a news analyst. Summarize the article into concise bullet points.

Output requirements (STRICT):
- Output ONLY markdown bullets (no title, no numbering, no headings).
- 3 to 5 bullets total.
- Each bullet must be <= 22 words.
- Include at least one concrete detail when available: date, number, person/org, location.
- If the article is unclear or low-quality, include one bullet: "Low confidence: limited reliable details found."

Article JSON:
{article_json}
"""

DIGEST_PROMPT = """You are producing a professional NEWS MONITORING DIGEST in MARKDOWN.

Audience: busy stakeholders (product, engineering, leadership).
Tone: neutral, factual, concise.

STRICT formatting rules:
- Use ONLY the section headers provided below, in the exact order.
- Use headings (##, ###) and bullet lists (-). Do NOT use ordered lists (1., 2., etc).
- Do NOT invent facts. Use only the provided summaries and URLs.
- Every article brief must include a URL.
- If a field is missing, write "Unknown" (do not guess).
- Keep the output stable and consistent across runs.

Data mapping (IMPORTANT):
- Each item in Input Summaries JSON has: title, url, published_date, source, summary.
- Use item.published_date for Date (or "Unknown").
- Use item.source for Source (or derive from the url domain if missing).
- Use item.summary bullets as the basis for "Why it matters" and "Key points" (condense as needed).
- Do not include any article that does not have a url.

Ordering:
- Sort Article Briefs by published_date (newest first). If published_date is "Unknown", place last.

------------------------------------------------------------
## News Monitoring Digest
- Topic: {topic}
- Time Window: last {window_hours} hours
- Generated At (UTC): {generated_at_utc}

## Executive Summary
- Provide exactly 3 bullets summarizing the most important developments.

## Key Themes
- Provide 3 to 5 bullets of recurring themes/patterns across articles.

## Alerts
- If there are urgent items, list 1 to 5 bullets.
- If none, write exactly: "- None"

Urgent criteria (use only if clearly supported):
- major security incident or breach
- new regulation / legal action / lawsuit
- major partnership or acquisition
- major service outage impacting many users
- significant market impact / sharp stock moves (if explicitly stated)

## Article Briefs
For EACH article, use this exact template:

### {{title}}
- Source: {{source}}
- Date: {{published_date_or_Unknown}}
- Why it matters:
  - 1 bullet (<= 22 words)
- Key points:
  - 2 bullets (each <= 22 words)
- Link: {{url}}

Notes:
- "Why it matters" must be a takeaway, not a repetition of the title.
- "Key points" should capture facts (who/what/when/impact).
- Avoid duplicates: if two items are the same story, keep the more credible source and drop the other.

## References
- List all URLs as bullets (no numbering). Include only unique links.
------------------------------------------------------------

Input Summaries JSON:
{summaries}
"""