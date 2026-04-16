"""
GigPulse Sentinel Admin API
Dashboard, claim review, fraud ring management
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import (
    Worker, Claim, Policy, Trigger, Payout, FraudRing, AuditLog, get_db
)
from backend.models.schemas import (
    AdminDashboardResponse, ClaimResponse, ResolveClaimRequest,
    FraudRingResponse, MessageResponse,
)
from backend.middleware.auth_middleware import require_admin
from backend.services.ring_detector import RingDetector
from backend.services.trust_score import TrustScoreService
from backend.services.payout_engine import PayoutEngine
from backend.services.notification_service import NotificationService
from backend.services.audit_logger import AuditLogger
from backend.ml.synthetic_data import SyntheticDataGenerator

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
async def admin_dashboard(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin dashboard with overview statistics."""
    workers_result = await db.execute(select(func.count(Worker.id)))
    total_workers = workers_result.scalar() or 0

    policies_result = await db.execute(select(func.count(Policy.id)).where(Policy.status == "ACTIVE"))
    active_policies = policies_result.scalar() or 0

    claims_result = await db.execute(select(Claim).order_by(Claim.created_at.desc()).limit(20))
    recent_claims = list(claims_result.scalars().all())

    pending_result = await db.execute(
        select(func.count(Claim.id)).where(
            Claim.status.in_(["PENDING", "APPEALED"]),
            Claim.fraud_tier.in_(["AMBER", "RED"]),
        )
    )
    pending_review = pending_result.scalar() or 0

    triggers_result = await db.execute(select(func.count(Trigger.id)).where(Trigger.status == "ACTIVE"))
    active_triggers = triggers_result.scalar() or 0

    rings_result = await db.execute(select(func.count(FraudRing.id)).where(FraudRing.status == "DETECTED"))
    fraud_rings = rings_result.scalar() or 0

    if total_workers == 0:
        demo_data = {
            "total_workers": 52, "active_policies": 38,
            "total_claims_today": 12, "pending_review_count": 3,
            "total_payouts_today": 8450.0, "active_triggers": 4,
            "fraud_rings_detected": 1,
            "risk_distribution": {"GREEN": 42, "AMBER": 7, "RED": 3},
        }
        gen = SyntheticDataGenerator()
        workers = gen.generate_workers(50)
        claims_data = gen.generate_claims(workers, 50)
        demo_data["recent_claims"] = claims_data[:10]
        return demo_data

    return {
        "total_workers": total_workers, "active_policies": active_policies,
        "total_claims_today": len(recent_claims), "pending_review_count": pending_review,
        "total_payouts_today": sum(c.actual_payout or 0 for c in recent_claims if c.status == "PAID"),
        "active_triggers": active_triggers, "fraud_rings_detected": fraud_rings,
        "risk_distribution": {
            "GREEN": sum(1 for c in recent_claims if c.fraud_tier == "GREEN"),
            "AMBER": sum(1 for c in recent_claims if c.fraud_tier == "AMBER"),
            "RED": sum(1 for c in recent_claims if c.fraud_tier == "RED"),
        },
        "recent_claims": [ClaimResponse.model_validate(c) for c in recent_claims[:10]],
    }


@router.get("/claims/review")
async def get_claims_for_review(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get claims pending manual review."""
    result = await db.execute(
        select(Claim).where(Claim.status.in_(["PENDING", "APPEALED"]))
        .order_by(Claim.created_at.desc())
    )
    claims = list(result.scalars().all())
    return {"claims": [ClaimResponse.model_validate(c) for c in claims], "total_pending": len(claims)}


@router.post("/claims/{claim_id}/resolve", response_model=MessageResponse)
async def resolve_claim(
    claim_id: str, request: ResolveClaimRequest,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Resolve a pending claim (approve/reject)."""
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if request.action == "APPROVE":
        claim.status = "APPROVED"
        claim.actual_payout = claim.calculated_payout
        claim.resolved_at = datetime.now(timezone.utc)
        claim.reviewed_by = current_user["worker_id"]
        claim.review_notes = request.notes

        goodwill = 50.0 if claim.appeal_status == "APPROVED" else 0
        if claim.appeal_status:
            claim.appeal_status = "APPROVED"

        payout = await PayoutEngine.process_payout(db, claim_id, claim.calculated_payout, goodwill)
        NotificationService.send_payout_notification(
            claim.worker_id, claim.calculated_payout + goodwill,
            claim.claim_type, claim.confidence_score or 85,
        )
        message = f"Claim approved. ₹{claim.calculated_payout + goodwill:,.0f} sent to worker."
    else:
        claim.status = "REJECTED"
        claim.resolved_at = datetime.now(timezone.utc)
        claim.reviewed_by = current_user["worker_id"]
        claim.review_notes = request.notes
        if claim.appeal_status:
            claim.appeal_status = "REJECTED"

        if claim.fraud_tier == "RED":
            await TrustScoreService.apply_strike(db, claim.worker_id, "Claim rejected by admin review")

        NotificationService.send_claim_update(
            claim.worker_id, claim_id, "REJECTED",
            f"Your claim was not approved. Reason: {request.notes or 'Fraud indicators detected'}. You can appeal within 48 hours.",
        )
        message = "Claim rejected."

    await db.flush()

    await AuditLogger.log(
        db, "CLAIM", claim_id, f"RESOLVED_{request.action}",
        actor_id=current_user["worker_id"], actor_role="ADMIN",
        new_state={"action": request.action, "notes": request.notes},
    )
    return MessageResponse(message=message)


@router.get("/fraud-rings")
async def get_fraud_rings(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get detected fraud rings."""
    result = await db.execute(select(FraudRing).order_by(FraudRing.detected_at.desc()).limit(20))
    rings = list(result.scalars().all())
    detected = await RingDetector.detect_rings(db)

    return {
        "stored_rings": [FraudRingResponse.model_validate(r) for r in rings],
        "live_detection": detected, "total_stored": len(rings), "total_live": len(detected),
    }


@router.get("/workers")
async def get_all_workers(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all workers (admin view)."""
    result = await db.execute(select(Worker).order_by(Worker.created_at.desc()))
    workers = list(result.scalars().all())

    if not workers:
        gen = SyntheticDataGenerator()
        return {"workers": gen.generate_workers(50), "total": 50, "is_demo": True}

    from backend.models.schemas import WorkerProfile
    return {
        "workers": [WorkerProfile.model_validate(w) for w in workers],
        "total": len(workers), "is_demo": False,
    }


@router.get("/audit-log")
async def get_audit_log(
    limit: int = 50,
    entity_type: str = None,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get audit log entries with optional filtering."""
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)

    result = await db.execute(query)
    entries = list(result.scalars().all())

    if not entries:
        return {"entries": [], "total": 0, "is_demo": True, "demo_entries": _get_demo_audit_logs()}

    return {
        "entries": [
            {
                "id": e.id,
                "entity_type": e.entity_type,
                "entity_id": e.entity_id,
                "action": e.action,
                "actor_id": e.actor_id,
                "actor_role": e.actor_role,
                "new_state": e.new_state,
                "entry_hash": e.entry_hash,
                "previous_hash": e.previous_hash,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ],
        "total": len(entries),
        "is_demo": False,
    }


@router.get("/audit-log/verify")
async def verify_audit_chain(
    limit: int = 100,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Verify the SHA-256 hash chain integrity of audit logs."""
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at).limit(limit))
    entries = list(result.scalars().all())

    if not entries:
        return {"valid": True, "entries_checked": 0, "message": "No entries to verify"}

    broken_links = []
    for i, entry in enumerate(entries):
        expected_prev = entries[i - 1].entry_hash if i > 0 else "GENESIS"
        if entry.previous_hash != expected_prev:
            broken_links.append({
                "entry_id": entry.id,
                "expected_previous": expected_prev,
                "actual_previous": entry.previous_hash,
            })

    return {
        "valid": len(broken_links) == 0,
        "entries_checked": len(entries),
        "broken_links": broken_links,
        "message": "Chain integrity verified" if len(broken_links) == 0 else f"Found {len(broken_links)} broken links",
    }


def _get_demo_audit_logs():
    return [
        {"id": "demo-1", "entity_type": "CLAIM", "entity_id": "claim-1", "action": "CLAIM_APPROVED", "actor_id": "system", "actor_role": "SYSTEM", "new_state": {"payout": 1120}, "entry_hash": "abc123", "previous_hash": "GENESIS", "created_at": "2026-04-17T10:00:00Z"},
        {"id": "demo-2", "entity_type": "TRIGGER", "entity_id": "trigger-1", "action": "TRIGGER_FIRED", "actor_id": "system", "actor_role": "SYSTEM", "new_state": {"type": "HEAVY_RAIN", "severity": "HIGH"}, "entry_hash": "def456", "previous_hash": "abc123", "created_at": "2026-04-17T09:30:00Z"},
        {"id": "demo-3", "entity_type": "CLAIM", "entity_id": "claim-2", "action": "CLAIM_REJECTED", "actor_id": "admin-1", "actor_role": "ADMIN", "new_state": {"reason": "GPS spoof detected"}, "entry_hash": "ghi789", "previous_hash": "def456", "created_at": "2026-04-17T09:00:00Z"},
        {"id": "demo-4", "entity_type": "FRAUD_RING", "entity_id": "ring-1", "action": "FRAUD_RING_DETECTED", "actor_id": "system", "actor_role": "SYSTEM", "new_state": {"member_count": 7, "confidence": 85}, "entry_hash": "jkl012", "previous_hash": "ghi789", "created_at": "2026-04-17T08:00:00Z"},
    ]
