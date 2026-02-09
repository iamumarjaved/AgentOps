.PHONY: install install-pip install-dev dev worker test test-cov lint format typecheck \
       docker-up docker-down migrate migrate-create seed generate-api-key \
       frontend-install frontend-dev clean

# ---- Install ----
install:
	uv sync

install-pip:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

# ---- Run (local) ----
dev:
	PYTHONPATH=src uv run uvicorn agentops.api.app:create_app --factory --reload --host 0.0.0.0 --port 8000

dev-pip:
	PYTHONPATH=src uvicorn agentops.api.app:create_app --factory --reload --host 0.0.0.0 --port 8000

worker:
	PYTHONPATH=src uv run celery -A agentops.workers.celery_app worker --loglevel=info

worker-pip:
	PYTHONPATH=src celery -A agentops.workers.celery_app worker --loglevel=info

# ---- Testing ----
test:
	PYTHONPATH=src uv run pytest tests/ -v --tb=short

test-pip:
	PYTHONPATH=src pytest tests/ -v --tb=short

test-cov:
	PYTHONPATH=src uv run pytest tests/ -v --tb=short --cov=src/agentops --cov-report=html

# ---- Code quality ----
lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/

typecheck:
	PYTHONPATH=src uv run mypy src/agentops/ --ignore-missing-imports

# ---- Docker ----
docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v

# ---- Database ----
migrate:
	PYTHONPATH=src uv run alembic upgrade head

migrate-create:
	PYTHONPATH=src uv run alembic revision --autogenerate -m "$(msg)"

# ---- Scripts ----
seed:
	PYTHONPATH=src uv run python scripts/seed_db.py

generate-api-key:
	PYTHONPATH=src uv run python scripts/generate_api_key.py

# ---- Frontend ----
frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

# ---- Cleanup ----
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info/ htmlcov/ .coverage
