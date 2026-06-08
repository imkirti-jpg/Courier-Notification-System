import uuid
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.dead_letter import DeadLetterJob
from app.models.notifications import Notification


#  used by the Celery worker 

def create_dead_letter_sync(
    db: Session,
    notification: Notification,
    error_message: str,
    attempt_count: int
) -> DeadLetterJob:
    job = DeadLetterJob(
        notification_id=notification.id,
        error_message=error_message,
        attempt_count=attempt_count
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# used by the FastAPI routes 

async def list_dead_letters(db: AsyncSession):
    result = await db.execute(
        select(DeadLetterJob).order_by(DeadLetterJob.created_at.desc())
    )
    return result.scalars().all()


async def get_dead_letter(db: AsyncSession, job_id: uuid.UUID):
    result = await db.execute(
        select(DeadLetterJob).where(DeadLetterJob.id == job_id)
    )
    return result.scalar_one_or_none()