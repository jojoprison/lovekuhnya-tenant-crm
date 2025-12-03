.PHONY: install up upb down b migrate migrate-new demo test test-cov smoke lint lint-fix clean help pre-commit

.DEFAULT_GOAL := help

help:
	@echo "LoveKuhnya Tenant CRM v1.0.0"
	@echo ""
	@echo "  setup:"
	@echo "    make install     - install dependencies (creates .venv)"
	@echo "    make pre-commit  - install pre-commit hooks"
	@echo ""
	@echo "  docker:"
	@echo "    make up          - start all services"
	@echo "    make upb         - start with rebuild"
	@echo "    make down        - stop all services"
	@echo "    make b           - build Docker image"
	@echo "    make clean       - stop and remove all data"
	@echo ""
	@echo "  database:"
	@echo "    make migrate     - run migrations (in container)"
	@echo "    make migrate-new - create migration (MSG=description)"
	@echo "    make demo        - load demo data (optional)"
	@echo ""
	@echo "  tests:"
	@echo "    make test        - run tests"
	@echo "    make test-cov    - run tests with coverage"
	@echo "    make smoke       - run API smoke tests (curl)"
	@echo ""
	@echo "  code quality:"
	@echo "    make lint        - check code (for CI)"
	@echo "    make lint-fix    - auto-fix code"


# creates .venv automatically
install:
	uv sync

pre-commit:
	uv run pre-commit install
	uv run pre-commit run --all-files


up:
	docker-compose up -d

upb:
	docker-compose up -d --build

down:
	docker-compose down

b:
	docker build -t lovekuhnya-tenant-crm:latest .

clean:
	docker-compose down -v


# run inside app container
migrate:
	docker-compose exec app uv run alembic upgrade head

migrate-new:
	docker-compose exec app uv run alembic revision --autogenerate -m "$(MSG)"

demo:
	docker-compose exec app uv run python -m src.scripts.seed


test-setup:
	docker-compose exec db psql -U postgres -c "CREATE DATABASE crm_test;" 2>/dev/null || true

test: test-setup
	docker-compose exec app uv run pytest -v

test-cov: test-setup
	docker-compose exec app uv run pytest --cov=src --cov-report=term -v

smoke:
	@./scripts/smoke_test.sh


# local with uv
lint:
	uv run ruff format --check src/ tests/
	uv run ruff check src/ tests/
	uv run mypy src/

lint-fix:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/
	uv run mypy src/
