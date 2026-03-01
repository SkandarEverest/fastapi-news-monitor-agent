dev:
	uv run uvicorn app.main:app --reload

celery:
	uv run celery -A app.celery_app worker --loglevel=info