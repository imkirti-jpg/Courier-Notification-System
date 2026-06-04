from pydantic import BaseModel, UUID4
from datetime import datetime

class TemplateCreate(BaseModel):
    name: str
    subject: str
    body: str

class TemplateUpdate(BaseModel):
    name: str | None = None
    subject: str | None = None
    body: str | None = None

class TemplateResponse(BaseModel):
    id: UUID4
    name: str
    subject: str
    body: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }