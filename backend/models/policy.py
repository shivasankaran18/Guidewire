"""
LaborGuard Pydantic Models — Policy
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


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
