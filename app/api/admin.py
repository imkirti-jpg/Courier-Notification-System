import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_db
from app.core.security import get_current_admin_user
from app.models.auth import User
from app.models.enums import NotificationStatus
from app.schemas.dead_letter import DeadLetterResponse, ReprocessResponse
from app.services import dead_letter_service
from app.services import notifications_service
from app.workers.tasks import send_notification

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dead-letters", response_model=list[DeadLetterResponse])
async def list_dead_letters(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin_user)
):
    return await dead_letter_service.list_dead_letters(db)


@router.post("/dead-letters/{job_id}/reprocess", response_model=ReprocessResponse)
async def reprocess(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin_user)
):
    # Load the dead letter job
    job = await dead_letter_service.get_dead_letter(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Dead letter job not found")

    # Load the original notification
    notification = await notifications_service.get_notification(db, job.notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # eset status to PENDING so the worker processes it fresh
    notification.status = NotificationStatus.PENDING
    await db.commit()

    # Re-queue
    send_notification.delay(str(notification.id))

    return ReprocessResponse(
        detail="Notification re-queued successfully",
        notification_id=notification.id
    )