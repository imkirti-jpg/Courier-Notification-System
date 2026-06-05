from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_db
from app.schemas.notifications import NotificationCreate, NotificationResponse
from app.services import notifications_service
from app.api.dependency import get_current_user
from app.models.auth import User
import uuid
from app.workers.tasks import send_notification 

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=NotificationResponse, status_code=202)
async def create_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        notification = await notifications_service.create_notification(
            db, data, current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    send_notification.delay(str(notification.id))

    return notification


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = await notifications_service.get_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return notification