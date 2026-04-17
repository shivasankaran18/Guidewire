"""
GigPulse Sentinel Claims API
Claim lifecycle management with fraud checking
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Claim, Policy, Trigger, Worker, get_db
from backend.models.schemas import (
    ClaimResponse, ClaimListResponse, AppealRequest, MessageResponse,
)
from backend.middleware.auth_middleware import get_current_user
from backend.services.fraud_detector import FraudDetector
from backend.services.payout_engine import PayoutEngine
from backend.services.notification_service import NotificationService
from backend.services.audit_logger import AuditLogger

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.get("/", response_model=ClaimListResponse)
async def get_claims(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all claims for the current worker."""
    result = await db.execute(
        select(Claim).where(Claim.worker_id == current_user["worker_id"])
        .order_by(Claim.created_at.desc())
    )
    claims = list(result.scalars().all())

    pending = sum(1 for c in claims if c.status == "PENDING")
    approved = sum(1 for c in claims if c.status in ("APPROVED", "PAID"))
    total_paid = sum(c.actual_payout or 0 for c in claims if c.status == "PAID")

    return ClaimListResponse(
        claims=[ClaimResponse.model_validate(c) for c in claims],
        total=len(claims), pending_count=pending,
        approved_count=approved, total_paid=round(total_paid, 2),
    )


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific claim details."""
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id, Claim.worker_id == current_user["worker_id"])
    )
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return ClaimResponse.model_validate(claim)


@router.post("/auto-claim/{trigger_id}", response_model=ClaimResponse)
async def auto_claim(
    trigger_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Automatically create a claim when a trigger fires."""
    result = await db.execute(select(Trigger).where(Trigger.id == trigger_id))
    trigger = result.scalar_one_or_none()
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    result = await db.execute(
        select(Policy).where(
            Policy.worker_id == current_user["worker_id"], Policy.status == "ACTIVE",
        ).order_by(Policy.created_at.desc()).limit(1)
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=400, detail="No active coverage policy")

    worker_result = await db.execute(select(Worker).where(Worker.id == current_user["worker_id"]))
    worker = worker_result.scalar_one_or_none()

    fraud_analysis = FraudDetector.generate_demo_analysis(is_genuine=True)

    disruption_hours = 4.0
    payout_calc = await PayoutEngine.calculate_payout(
        db, worker_id=current_user["worker_id"], policy_id=policy.id,
        trigger_type=trigger.trigger_type, disruption_hours=disruption_hours,
    )

    claim = Claim(
        id=str(uuid.uuid4()), worker_id=current_user["worker_id"],
        policy_id=policy.id, trigger_id=trigger_id,
        zone_code=trigger.zone_code, claim_type=trigger.trigger_type,
        disruption_hours=disruption_hours, working_hours=10.0,
        earnings_for_slot=payout_calc["earnings_for_slot"],
        calculated_payout=payout_calc["calculated_payout"],
        payout_cap=payout_calc["payout_cap"],
        fraud_score=fraud_analysis["fraud_score"],
        fraud_tier=fraud_analysis["fraud_tier"],
        confidence_score=fraud_analysis["confidence_score"],
        fraud_signals=fraud_analysis["signals"],
        verification_method=fraud_analysis["verification_method"],
    )

    if fraud_analysis["fraud_tier"] == "GREEN":
        claim.status = "APPROVED"
        claim.actual_payout = payout_calc["actual_payout"]
        claim.resolved_at = datetime.now(timezone.utc)

        db.add(claim)
        await db.flush()

        payout = await PayoutEngine.process_payout(db, claim.id, payout_calc["actual_payout"])
        await NotificationService.send_payout_notification(
            db,
            current_user["worker_id"],
            payout_calc["actual_payout"],
            trigger.trigger_type,
            fraud_analysis["confidence_score"],
            claim_id=claim.id,
        )
    else:
        claim.status = "PENDING"
        db.add(claim)
        await db.flush()

    await AuditLogger.log(
        db, "CLAIM", claim.id, "CREATED",
        actor_id=current_user["worker_id"],
        new_state={"trigger": trigger.trigger_type, "fraud_tier": fraud_analysis["fraud_tier"], "payout": payout_calc["actual_payout"]},
    )
    return ClaimResponse.model_validate(claim)


@router.post("/appeal/{claim_id}", response_model=MessageResponse)
async def appeal_claim(
    claim_id: str, request: AppealRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Appeal a rejected or held claim."""
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id, Claim.worker_id == current_user["worker_id"])
    )
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim.status not in ("REJECTED", "PENDING"):
        raise HTTPException(status_code=400, detail=f"Cannot appeal a {claim.status} claim")

    claim.appeal_status = "PENDING"
    claim.appeal_reason = request.reason
    claim.status = "APPEALED"
    await db.flush()

    await AuditLogger.log(
        db, "CLAIM", claim_id, "APPEALED",
        actor_id=current_user["worker_id"],
        new_state={"reason": request.reason},
    )

    await NotificationService.send_claim_update(
        db,
        current_user["worker_id"],
        claim_id,
        "APPEALED",
        "Your appeal has been submitted. Manual review within 2 hours.",
    )
    return MessageResponse(message="Appeal submitted successfully. You'll hear back within 2 hours.")
