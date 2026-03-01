import os
from dotenv import load_dotenv
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.modules.news.schema import MonitorInput
from app.modules.news.tasks import monitor_news_task

load_dotenv()

app = FastAPI(title="News Monitoring Agent")

@app.post("/monitor")
def start_monitoring(body: MonitorInput):
    task = monitor_news_task.delay(body.model_dump())  # type: ignore
    return {"task_id": task.id, "message": "Processing!"}

@app.get("/monitor/{task_id}/status")
def get_status(task_id: str):
    from celery.result import AsyncResult
    from app.celery_app import celery_app
    r = AsyncResult(task_id, app=celery_app)
    return {"task_id": task_id, "state": r.state}

@app.get("/monitor/{task_id}/result")
def get_result(task_id: str):
    from celery.result import AsyncResult
    from app.celery_app import celery_app
    r = AsyncResult(task_id, app=celery_app)
    if not r.ready():
        return {"task_id": task_id, "state": r.state, "result": None}
    return {"task_id": task_id, "state": r.state, "result": r.result}

@app.get("/scalar")
def scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)

@app.get("/health")
def health():
    return {"ok": True}