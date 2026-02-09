.PHONY: install dev test lint format typecheck docker-up docker-down migrate seed clean

install:
	uv sync

dev:
	uv run uvicorn src.agentops.api.app:create_app --factory --reload --host 0.0.0.0 --port 8000

worker:
	uv run celery -A src.agentops.workers.celery_app worker --loglevel=info

test:
	uv run pytest tests/ -v --tb=short

test-cov:
	uv run pytest tests/ -v --tb=short --cov=src/agentops --cov-report=html

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/

typecheck:
	uv run mypy src/agentops/

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v

migrate:
	uv run alembic upgrade head

migrate-create:
	uv run alembic revision --autogenerate -m "$(msg)"

seed:
	uv run python scripts/seed_db.py

generate-api-key:
	uv run python scripts/generate_api_key.py

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info/ htmlcov/ .coverage
