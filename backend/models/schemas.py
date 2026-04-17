"""
LaborGuard Pydantic Schemas
Request/Response models for all API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============================================
# AUTH SCHEMAS
# ============================================
class SendOTPRequest(BaseModel):
    phone: str = Field(..., min_length=10, description="Indian phone number with or without +91 prefix")


class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., min_length=10)
    otp: str = Field(..., min_length=6, max_length=6)
    device_fingerprint: Optional[str] = None


class RegisterRequest(BaseModel):
    phone: str = Field(..., min_length=10)
    name: str = Field(..., min_length=2, max_length=200)
    platform: str = Field(..., pattern=r"^(zomato|swiggy)$")
    platform_worker_id: str = Field(..., min_length=3)
    aadhaar_last4: Optional[str] = Field(None, min_length=4, max_length=4)
    upi_id: Optional[str] = None
    device_fingerprint: Optional[str] = None
    device_model: Optional[str] = None
    zone_code: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    worker_id: str
    role: str
    name: str


class OTPResponse(BaseModel):
    message: str
    expires_in_seconds: int = 300


# ============================================
# WORKER SCHEMAS
# ============================================
class WorkerProfile(BaseModel):
    id: str
    phone: str
    name: str
    platform: str
    platform_worker_id: str
    email: Optional[str] = None
    aadhaar_last4: Optional[str] = None
    upi_id_masked: Optional[str] = None
    device_model: Optional[str] = None
    primary_zone_code: Optional[str] = None
    avg_daily_earnings: float
    avg_weekly_earnings: float
    tenure_weeks: int
    trust_score: float
    is_verified_partner: bool
    fraud_strikes: int
    account_status: str
    role: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkerUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    upi_id: Optional[str] = None
    zone_code: Optional[str] = None
    device_fingerprint: Optional[str] = None


# ============================================
# NOTIFICATION SCHEMAS
# ============================================
class NotificationItem(BaseModel):
    id: str
    title: str
    message: str
    type: str
    data: dict = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None


class NotificationListResponse(BaseModel):
    notifications: list[NotificationItem]


class MarkReadResponse(BaseModel):
    success: bool = True


class UnreadCountResponse(BaseModel):
    unread_count: int


class TrustScoreResponse(BaseModel):
    worker_id: str
    trust_score: float
    is_verified_partner: bool
    clean_claims: int
    total_claims: int
    fraud_strikes: int
    account_status: str
    badge: Optional[str] = None


# ============================================
# POLICY SCHEMAS
# ============================================
class PlanTier(BaseModel):
    tier: str
    name: str
    premium_range: str
    coverage_multiplier: float
    description: str
    features: list[str]


class PlanListResponse(BaseModel):
    plans: list[PlanTier]
    worker_zone_risk: Optional[str] = None
    recommended_plan: Optional[str] = None


class ActivatePolicyRequest(BaseModel):
    plan_tier: str = Field(..., pattern=r"^(BASIC|STANDARD|PREMIUM)$")
    payment_method: str = Field(default="UPI")
    upi_reference: Optional[str] = None


class PolicyResponse(BaseModel):
    id: str
    plan_tier: str
    premium_amount: float
    coverage_amount: float
    coverage_multiplier: float
    week_start: str
    week_end: str
    status: str
    payment_status: str
    risk_factors: Optional[dict] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CurrentPolicyResponse(BaseModel):
    has_active_policy: bool
    policy: Optional[PolicyResponse] = None
    premium_prediction: Optional[dict] = None


# ============================================
# TRIGGER SCHEMAS
# ============================================
class TriggerStatus(BaseModel):
    id: str
    zone_code: str
    trigger_type: str
    severity: str
    threshold_value: Optional[float] = None
    threshold_limit: Optional[float] = None
    sources_agreeing: int
    auto_approved: bool
    triggered_at: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True


class TriggerStatusResponse(BaseModel):
    zone_code: str
    active_triggers: list[TriggerStatus]
    weather_current: Optional[dict] = None
    aqi_current: Optional[dict] = None
    platform_status: Optional[dict] = None


# ============================================
# CLAIM SCHEMAS
# ============================================
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


# ============================================
# ADMIN SCHEMAS
# ============================================
class AdminDashboardResponse(BaseModel):
    total_workers: int
    active_policies: int
    total_claims_today: int
    pending_review_count: int
    total_payouts_today: float
    active_triggers: int
    fraud_rings_detected: int
    risk_distribution: dict
    recent_claims: list[ClaimResponse]


class AdminClaimReviewResponse(BaseModel):
    claims: list[ClaimResponse]
    total_pending: int


class ResolveClaimRequest(BaseModel):
    action: str = Field(..., pattern=r"^(APPROVE|REJECT)$")
    notes: Optional[str] = None
    co_signer_id: Optional[str] = None


class FraudRingResponse(BaseModel):
    id: str
    ring_id: str
    member_count: int
    detection_method: Optional[str] = None
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None
    radius_meters: Optional[int] = None
    member_worker_ids: list[str]
    shared_signals: Optional[dict] = None
    status: str
    frozen_amount: float
    detected_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# EARNINGS DNA SCHEMAS
# ============================================
class EarningsDNASlot(BaseModel):
    day_of_week: int
    hour_slot: int
    avg_earnings: float
    order_count: int


class EarningsDNAResponse(BaseModel):
    worker_id: str
    patterns: list[EarningsDNASlot]
    peak_day: str
    peak_hour: int
    avg_daily: float
    avg_weekly: float


# ============================================
# PAYOUT SCHEMAS
# ============================================
class PayoutResponse(BaseModel):
    id: str
    claim_id: str
    amount: float
    upi_reference: Optional[str] = None
    payment_status: str
    goodwill_credit: float
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# GENERIC SCHEMAS
# ============================================
class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
