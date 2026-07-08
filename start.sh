#!/bin/sh
set -e

echo "Executing database migrations..."
alembic upgrade head

# 2. Launch Celery worker in the background (using the & operator)
echo "Starting background Celery worker..."
celery -A app.workers.celery_app worker --loglevel=info &

# 3. Start FastAPI in the foreground (Render monitors this process)
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT