# Courier

Courier is a FastAPI-based notification system for sending templated email notifications asynchronously. It uses PostgreSQL for storage, Redis for caching and queueing, and Celery workers to send emails in the background.

## What It Does

- User authentication with JWT
- CRUD for reusable notification templates
- Create and track notifications per user
- Background delivery through Celery
- Retry handling and dead-letter tracking
- Analytics with Redis caching
- Health check for database and Redis

## Tech Stack

- FastAPI
- PostgreSQL
- Redis
- Celery
- SQLAlchemy 2.0 async
- Alembic
- Jinja2
- Passlib + python-jose
- Mailhog or SendGrid for email delivery

## Project Structure

- `app/main.py` - FastAPI app and router registration
- `app/api/` - HTTP routes
- `app/core/` - config, security, logging, rate limiting
- `app/db/` - database and Redis connections
- `app/models/` - SQLAlchemy models
- `app/schemas/` - Pydantic request/response schemas
- `app/services/` - business logic
- `app/utils/` - template rendering helpers
- `app/workers/` - Celery app and tasks
- `alembic/` - database migrations

## Main Features

### Auth

- `POST /auth/register` creates a user
- `POST /auth/login` returns a JWT access token
- `GET /auth/me` returns the current user

### Templates

- `POST /templates/`
- `GET /templates/`
- `PUT /templates/{template_id}`
- `DELETE /templates/{template_id}`

Template bodies are validated as Jinja2 before saving.

### Notifications

- `POST /notifications/` creates a notification and queues it for delivery
- `GET /notifications/{notification_id}` fetches one notification

Notification statuses include `PENDING`, `PROCESSING`, `SENT`, `FAILED`, `RETRYING`, and `SKIPPED`.

### Admin

- `GET /admin/dead-letters` lists failed jobs
- `POST /admin/dead-letters/{job_id}/reprocess` queues a failed notification again

### Analytics

- `GET /analytics/` returns delivery and retry metrics
- Optional filters: `from_date`, `to_date`
- Results are cached in Redis for 60 seconds

### Health Check

- `GET /health` checks PostgreSQL and Redis

## How It Works

1. A user creates a notification request.
2. The API saves it in PostgreSQL with status `PENDING`.
3. The notification ID is sent to Celery.
4. The worker loads the notification and template, renders the content, and sends email.
5. The status becomes `SENT`, or `RETRYING` / `FAILED` if delivery fails.

## Required Environment Variables

Create a `.env` file with at least:

```env
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/notifications
CELERY_DATABASE_URL=postgresql+psycopg2://user:password@postgres:5432/notifications
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change-me
EMAIL_FROM=no-reply@example.com
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SENDGRID_API_KEY=
```

`ACCESS_TOKEN_EXPIRE_MINUTES` is optional and defaults to `60`.

## Local Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/Scripts/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

### 5. Start the Celery worker

```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## Docker Setup

The app also runs with Docker Compose:

```bash
docker compose up --build
```

This starts:

- API on port `8000`
- PostgreSQL on port `5432`
- Redis on port `6379`
- Mailhog on ports `1025` and `8025`
- Celery worker in a separate container

## Notes

- Login uses form data, not JSON.
- Some routes require an authenticated user, and admin routes require `is_admin = true`.
- The worker retries failed email jobs and writes final failures to the dead-letter table.
- The startup script runs migrations, starts Celery in the background, and launches Uvicorn.

## Useful Endpoints

- `GET /health`
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `POST /templates/`
- `GET /templates/`
- `POST /notifications/`
- `GET /notifications/{notification_id}`
- `GET /analytics/`
- `GET /admin/dead-letters`
