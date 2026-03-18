.PHONY: install dev test lint format gateway

install:
	uv sync

dev:
	uv run python -m jobflow

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check .

format:
	uv run ruff format .

gateway:
	uv run uvicorn app.gateway.app:app --host 0.0.0.0 --port 8001 --reload
