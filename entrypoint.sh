#!/bin/bash
set -e

echo "running migrations..."
uv run alembic upgrade head

echo "starting app..."
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
