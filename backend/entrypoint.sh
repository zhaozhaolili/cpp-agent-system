#!/bin/bash
set -e

echo "==> Initializing database..."
python scripts/init_db.py

echo "==> Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
