from pydantic import BaseModel
from datetime import date

class DailyBreakdown(BaseModel):
    date: date
    sent: int
    failed: int
    total: int

class TopTemplate(BaseModel):
    template_name: str
    count: int

class AnalyticsResponse(BaseModel):
    total_sent: int
    total_failed: int
    delivery_rate: float          # percentage, 0–100
    retry_rate: float             # percentage of all notifications
    daily_breakdown: list[DailyBreakdown]
    top_templates: list[TopTemplate]