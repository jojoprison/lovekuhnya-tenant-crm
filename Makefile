.PHONY: install up upb down b migrate migrate-new seed test test-cov lint format typecheck clean help

help:
	@echo "commands"
	@echo ""
	@echo "  setup:"
	@echo "    make install     - install dependencies (creates .venv)"
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
	@echo "    make seed        - seed demo data"
	@echo ""
	@echo "  tests:"
	@echo "    make test        - run tests"
	@echo "    make test-cov    - run tests with coverage"
	@echo ""
	@echo "  code quality:"
	@echo "    make lint        - check code (ruff)"
	@echo "    make format      - format code (black + isort)"
	@echo "    make typecheck   - type check (mypy)"


# creates .venv automatically
install:
	uv sync


up:
	docker-compose up -d

upb:
	docker-compose up -d --build

down:
	docker-compose down

b:
	docker build -t mini-crm:latest .

clean:
	docker-compose down -v


# run inside app container
migrate:
	docker-compose exec app alembic upgrade head

migrate-new:
	docker-compose exec app alembic revision --autogenerate -m "$(MSG)"

seed:
	docker-compose exec app python -m src.scripts.seed


test-setup:
	docker-compose exec db psql -U postgres -c "CREATE DATABASE crm_test;" 2>/dev/null || true

test: test-setup
	docker-compose exec app pytest -v

test-cov: test-setup
	docker-compose exec app pytest --cov=src --cov-report=term -v


# local with uv
lint:
	uv run ruff check src/

format:
	uv run black src/ tests/
	uv run isort src/ tests/

typecheck:
	uv run mypy src/
