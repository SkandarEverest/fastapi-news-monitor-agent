# 📰 News Monitoring Agent

Agentic workflow project built with **FastAPI + Celery + Tavily +
OpenRouter/OpenAI**.

This system monitors recent news on a topic, summarizes articles, and
generates a structured digest in **JSON, Markdown, and PDF** format.

------------------------------------------------------------------------

## 🚀 Features

-   Agentic workflow (7 steps)
-   Web search using Tavily API
-   Article summarization using LL
-   Structured monitoring digest
-   Async background processing with Celery
-   PDF export
-   API testing via Scalar

------------------------------------------------------------------------

## 🧠 Agentic Workflow

1.  Validate input (topic, keywords, time window)
2.  Generate search queries (LLM)
3.  Retrieve recent news (Tavily)
4.  Deduplicate and filter articles
5.  Summarize each article (LLM)
6.  Generate structured digest (LLM)
7.  Export JSON, Markdown, and PDF

------------------------------------------------------------------------

## 🛠 Tech Stack

-   FastAPI
-   Celery
-   Redis
-   Tavily API
-   OpenRouter / OpenAI
-   WeasyPrint

------------------------------------------------------------------------

## ⚙️ Setup

### 1. Install dependencies

``` bash
uv sync
```

### 2. Create `.env`

Copy template:

``` bash
cp .env.example .env
```

Add your keys:

    TAVILY_API_KEY=your_tavily_key
    OPENAI_API_KEY=your_key
    OPENAI_BASE_URL=https://openrouter.ai/api/v1
    OPENAI_MODEL=openai/gpt-4o-mini

------------------------------------------------------------------------

### 3. Start Redis

``` bash
docker run -p 6379:6379 redis:7-alpine
```

------------------------------------------------------------------------

### 4. Start Celery worker

``` bash
make celery
```

------------------------------------------------------------------------

### 5. Start FastAPI server

``` bash
make dev
```

------------------------------------------------------------------------

## 🧪 Test the API

Open:

http://127.0.0.1:8000/scalar

### Example request

POST `/monitor`

``` json
{
  "topic": "AI regulation",
  "keywords": ["EU AI Act", "OpenAI"],
  "window_hours": 48,
  "max_articles": 8
}
```

Then:

-   GET `/monitor/{task_id}/status`
-   GET `/monitor/{task_id}/result`

------------------------------------------------------------------------

## 📂 Output

Generated files are saved in:

    /outputs/

Each run creates:

-   `.json`
-   `.md`
-   `.pdf`
