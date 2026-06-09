import json
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_db
from app.db.redis import redis_client
from app.core.security import get_current_user
from app.models.auth import User
from app.schemas.analytics import AnalyticsResponse
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])

CACHE_TTL = 60   # seconds


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    from_date: date | None = Query(default=None, description="Filter from this date"),
    to_date: date | None = Query(default=None, description="Filter to this date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ── 1. Build a deterministic cache key from the filters ───────────────
    cache_key = f"analytics:{current_user.id}:{from_date}:{to_date}"

    # ── 2. Return cached result if available ──────────────────────────────
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # ── 3. Compute fresh metrics ──────────────────────────────────────────
    result = await analytics_service.compute_analytics(db, from_date, to_date)

    # ── 4. Cache for 60 seconds ───────────────────────────────────────────
    await redis_client.setex(cache_key, CACHE_TTL, json.dumps(result, default=str))

    return result