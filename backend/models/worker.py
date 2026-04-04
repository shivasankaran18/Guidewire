"""
LaborGuard Pydantic Models — Worker
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WorkerBase(BaseModel):
    phone: str = Field(..., pattern=r"^\+91\d{10}$")
    name: str = Field(..., min_length=2, max_length=200)
    platform: str = Field(..., pattern=r"^(zomato|swiggy)$")
    platform_worker_id: str = Field(..., min_length=3)


class WorkerCreate(WorkerBase):
    aadhaar_last4: Optional[str] = Field(None, min_length=4, max_length=4)
    upi_id: Optional[str] = None
    device_fingerprint: Optional[str] = None
    device_model: Optional[str] = None
    zone_code: Optional[str] = None


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    upi_id: Optional[str] = None
    zone_code: Optional[str] = None
    device_fingerprint: Optional[str] = None


class WorkerProfile(BaseModel):
    id: str
    phone: str
    name: str
    platform: str
    platform_worker_id: str
    aadhaar_last4: Optional[str] = None
    upi_id_masked: Optional[str] = None
    device_model: Optional[str] = None
    primary_zone_code: Optional[str] = None
    avg_daily_earnings: float = 0
    avg_weekly_earnings: float = 0
    tenure_weeks: int = 0
    trust_score: float = 50.0
    is_verified_partner: bool = False
    fraud_strikes: int = 0
    account_status: str = "PROBATION"
    role: str = "WORKER"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TrustScoreResponse(BaseModel):
    worker_id: str
    trust_score: float
    is_verified_partner: bool
    clean_claims: int = 0
    total_claims: int = 0
    fraud_strikes: int = 0
    account_status: str = "ACTIVE"
    badge: Optional[str] = None
