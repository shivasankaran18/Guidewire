"""
GigPulse Sentinel Payouts API
Payout processing via Razorpay mock UPI
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Claim, Payout, Worker, get_db
from backend.middleware.auth_middleware import get_current_user, require_admin
from backend.services.audit_logger import AuditLogger

router = APIRouter(prefix="/payouts", tags=["Payouts"])


@router.get("/")
async def get_my_payouts(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all payouts for the current worker."""
    result = await db.execute(
        select(Payout).where(Payout.worker_id == current_user["worker_id"])
        .order_by(Payout.created_at.desc())
    )
    payouts = list(result.scalars().all())

    total_received = sum(p.amount for p in payouts if p.payment_status == "COMPLETED")
    total_goodwill = sum(p.goodwill_credit or 0 for p in payouts)

    return {
        "payouts": [
            {
                "id": p.id, "claim_id": p.claim_id, "amount": p.amount,
                "upi_reference": p.upi_reference, "payment_status": p.payment_status,
                "goodwill_credit": p.goodwill_credit or 0,
                "paid_at": p.paid_at.isoformat() if p.paid_at else None,
            }
            for p in payouts
        ],
        "total_received": round(total_received, 2),
        "total_goodwill": round(total_goodwill, 2),
        "payout_count": len(payouts),
    }


@router.get("/{payout_id}")
async def get_payout_detail(
    payout_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific payout detail."""
    result = await db.execute(
        select(Payout).where(Payout.id == payout_id, Payout.worker_id == current_user["worker_id"])
    )
    payout = result.scalar_one_or_none()
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")

    return {
        "id": payout.id, "claim_id": payout.claim_id, "amount": payout.amount,
        "upi_reference": payout.upi_reference, "payment_method": payout.payment_method,
        "payment_status": payout.payment_status,
        "goodwill_credit": payout.goodwill_credit or 0,
        "total": payout.amount + (payout.goodwill_credit or 0),
        "paid_at": payout.paid_at.isoformat() if payout.paid_at else None,
    }


@router.post("/process/{claim_id}")
async def process_payout(
    claim_id: str,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: manually process a payout for an approved claim."""
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim.status != "APPROVED":
        raise HTTPException(status_code=400, detail=f"Claim is {claim.status}, not APPROVED")

    existing = await db.execute(select(Payout).where(Payout.claim_id == claim_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Payout already processed for this claim")

    payout = Payout(
        id=str(uuid.uuid4()), claim_id=claim_id, worker_id=claim.worker_id,
        amount=claim.calculated_payout,
        upi_reference=f"UPI_{uuid.uuid4().hex[:12].upper()}",
        payment_method="UPI", payment_status="COMPLETED",
        paid_at=datetime.now(timezone.utc),
    )
    db.add(payout)

    claim.status = "PAID"
    claim.actual_payout = claim.calculated_payout
    claim.paid_at = datetime.now(timezone.utc)
    await db.flush()

    await AuditLogger.log(
        db, "PAYOUT", payout.id, "PROCESSED",
        actor_id=current_user["worker_id"], actor_role="ADMIN",
        new_state={"amount": payout.amount, "claim_id": claim_id},
    )

    return {
        "message": f"Payout of ₹{payout.amount:,.0f} processed successfully",
        "payout_id": payout.id, "upi_reference": payout.upi_reference,
    }
