from pydantic import BaseModel, EmailStr, UUID4
from datetime import datetime
from typing import Any
from app.models.enums import NotificationStatus

class NotificationCreate(BaseModel):
    template_id: UUID4
    recipient: EmailStr        
    payload: dict[str, Any] = {}
    send_at: datetime | None = None

class NotificationResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    template_id: UUID4
    recipient: str
    payload: dict[str, Any]
    status: NotificationStatus
    send_at: datetime | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }