.DEFAULT_GOAL := help
.PHONY: help install dev run test lint format typecheck check clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

dev: install ## Run the dev server with auto-reload
	uv run fastapi dev app/main.py

run: install ## Run the production server
	uv run fastapi run app/main.py

test: ## Run tests
	uv run pytest

lint: ## Lint with ruff
	uv run ruff check .
	uv run ruff format --check .

format: ## Auto-format and fix lint issues
	uv run ruff check --fix .
	uv run ruff format .

typecheck: ## Type-check with mypy
	uv run mypy

check: lint typecheck test ## Run lint, typecheck and tests

clean: ## Remove caches and build artifacts
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache \) -prune -exec rm -rf {} +
