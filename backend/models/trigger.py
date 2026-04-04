"""
LaborGuard Pydantic Models — Trigger
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TriggerStatus(BaseModel):
    id: str
    zone_code: str
    trigger_type: str
    severity: str
    threshold_value: Optional[float] = None
    threshold_limit: Optional[float] = None
    sources_agreeing: int = 0
    auto_approved: bool = False
    triggered_at: Optional[datetime] = None
    status: str = "ACTIVE"

    class Config:
        from_attributes = True


class TriggerStatusResponse(BaseModel):
    zone_code: str
    active_triggers: list[TriggerStatus]
    weather_current: Optional[dict] = None
    aqi_current: Optional[dict] = None
    platform_status: Optional[dict] = None
