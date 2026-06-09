from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.db import SessionLocal
from app.db.redis import redis_client

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():

    db_status = "up"
    redis_status = "up"

    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "down"

    try:
        await redis_client.ping()
    except Exception:
        redis_status = "down"

    healthy = db_status == "up" and redis_status == "up"

    return JSONResponse(
        status_code=200 if healthy else 503,
        content={
            "status": "healthy" if healthy else "unhealthy",
            "database": db_status,
            "redis": redis_status,
        },
    )