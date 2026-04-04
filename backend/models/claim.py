"""
LaborGuard Pydantic Models — Claim
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ClaimResponse(BaseModel):
    id: str
    claim_type: str
    zone_code: str
    disruption_hours: float
    calculated_payout: float
    actual_payout: Optional[float] = None
    confidence_score: Optional[float] = None
    fraud_tier: Optional[str] = None
    verification_method: Optional[str] = None
    status: str
    appeal_status: Optional[str] = None
    claimed_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClaimListResponse(BaseModel):
    claims: list[ClaimResponse]
    total: int
    pending_count: int
    approved_count: int
    total_paid: float


class AppealRequest(BaseModel):
    reason: str = Field(..., min_length=10, max_length=500)


class ResolveClaimRequest(BaseModel):
    action: str = Field(..., pattern=r"^(APPROVE|REJECT)$")
    notes: Optional[str] = None
    co_signer_id: Optional[str] = None
