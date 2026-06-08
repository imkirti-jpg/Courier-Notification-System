import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.db import Base

class DeadLetterJob(Base):
    __tablename__ = "dead_letter_jobs"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("notifications.id"), nullable=False)
    error_message : Mapped[str] = mapped_column(Text, nullable=False)
    attempt_count : Mapped[int] = mapped_column(Integer, nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)