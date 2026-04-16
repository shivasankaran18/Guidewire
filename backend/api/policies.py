"""
GigPulse Sentinel Policies API
Weekly coverage plan management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Policy, Worker, get_db
from backend.models.schemas import (
    ActivatePolicyRequest, PolicyResponse, CurrentPolicyResponse,
    PlanListResponse, PlanTier, MessageResponse,
)
from backend.middleware.auth_middleware import get_current_user
from backend.services.premium_engine import PremiumEngine
from backend.services.audit_logger import AuditLogger

router = APIRouter(prefix="/policies", tags=["Policies"])


@router.get("/plans", response_model=PlanListResponse)
async def get_plans(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get available plan tiers with pricing."""
    plans_data = PremiumEngine.get_plan_tiers()
    plans = [PlanTier(**p) for p in plans_data]

    result = await db.execute(select(Worker).where(Worker.id == current_user["worker_id"]))
    worker = result.scalar_one_or_none()
    zone_risk = "MEDIUM"
    recommended = "STANDARD"

    if worker and worker.primary_zone_code:
        from backend.services.zone_engine import ZoneEngine
        zone = await ZoneEngine.get_zone_by_code(db, worker.primary_zone_code)
        if zone:
            risk_info = ZoneEngine.calculate_overall_risk(zone)
            zone_risk = risk_info["risk_level"]
            if zone_risk in ("HIGH", "CRITICAL"):
                recommended = "PREMIUM"
            elif zone_risk == "LOW":
                recommended = "BASIC"

    return PlanListResponse(
        plans=plans, worker_zone_risk=zone_risk,
        recommended_plan=recommended,
    )


@router.get("/current", response_model=CurrentPolicyResponse)
async def get_current_policy(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get worker's current active policy."""
    result = await db.execute(
        select(Policy).where(
            Policy.worker_id == current_user["worker_id"],
            Policy.status == "ACTIVE",
        ).order_by(Policy.created_at.desc()).limit(1)
    )
    policy = result.scalar_one_or_none()

    if not policy:
        try:
            prediction = await PremiumEngine.calculate_premium(db, current_user["worker_id"], "STANDARD")
        except Exception:
            prediction = None
        return CurrentPolicyResponse(has_active_policy=False, premium_prediction=prediction)

    return CurrentPolicyResponse(
        has_active_policy=True,
        policy=PolicyResponse.model_validate(policy),
    )


@router.post("/activate", response_model=PolicyResponse)
async def activate_policy(
    request: ActivatePolicyRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Activate a weekly coverage policy."""
    result = await db.execute(
        select(Policy).where(
            Policy.worker_id == current_user["worker_id"],
            Policy.status == "ACTIVE",
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an active policy this week. Wait until it expires.",
        )

    policy = await PremiumEngine.create_policy(
        db, worker_id=current_user["worker_id"],
        plan_tier=request.plan_tier, payment_reference=request.upi_reference,
    )

    await AuditLogger.log(
        db, "POLICY", policy.id, "ACTIVATED",
        actor_id=current_user["worker_id"],
        new_state={"plan_tier": request.plan_tier, "premium": policy.premium_amount, "coverage": policy.coverage_amount},
    )
    return PolicyResponse.model_validate(policy)


@router.get("/history", response_model=list[PolicyResponse])
async def get_policy_history(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get worker's policy history."""
    result = await db.execute(
        select(Policy).where(Policy.worker_id == current_user["worker_id"])
        .order_by(Policy.created_at.desc()).limit(20)
    )
    policies = result.scalars().all()
    return [PolicyResponse.model_validate(p) for p in policies]
