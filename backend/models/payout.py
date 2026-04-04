"""
LaborGuard Pydantic Models — Payout
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PayoutRequest(BaseModel):
    claim_id: str
    amount: float
    upi_id: Optional[str] = None


class PayoutResponse(BaseModel):
    id: str
    claim_id: str
    amount: float
    upi_reference: Optional[str] = None
    payment_status: str
    goodwill_credit: float = 0
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FraudRingResponse(BaseModel):
    id: str
    ring_id: str
    member_count: int
    detection_method: Optional[str] = None
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None
    radius_meters: Optional[int] = None
    member_worker_ids: list[str]
    status: str
    frozen_amount: float
    detected_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class SendOTPRequest(BaseModel):
    phone: str

class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str
    device_fingerprint: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    worker_id: str
    role: str
    name: str

class OTPResponse(BaseModel):
    message: str
    expires_in_seconds: int = 300
