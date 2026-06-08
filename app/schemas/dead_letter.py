from pydantic import BaseModel, UUID4
from datetime import datetime

class DeadLetterResponse(BaseModel):
    id: UUID4
    notification_id: UUID4
    error_message: str
    attempt_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReprocessResponse(BaseModel):
    detail: str
    notification_id: UUID4