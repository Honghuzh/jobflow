.PHONY: install dev test lint format

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
