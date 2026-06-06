from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.notifications import Notification
from app.models.templates import Template
from app.models.enums import NotificationStatus
from app.schemas.notifications import NotificationCreate
import uuid

async def create_notification(
    db: AsyncSession,
    data: NotificationCreate,
    user_id: uuid.UUID
):
    # Validate the template actually exists
    result = await db.execute(select(Template).where(Template.id == data.template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise ValueError("Template not found")

    notification = Notification(
        user_id=user_id,
        template_id=data.template_id,
        recipient=data.recipient,
        payload=data.payload,
        status=NotificationStatus.PENDING,
        send_at=data.send_at,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification

async def get_notification(db: AsyncSession, notification_id: uuid.UUID):
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    return result.scalar_one_or_none()


async def get_notifications(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(
        select(Notification).where(Notification.user_id == user_id)
    )
    return result.scalars().all()