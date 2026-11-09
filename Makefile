.PHONY: install run lint format build

install:
	uv sync

run:
	uv run database

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .

build:
	uv build

