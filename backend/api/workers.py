"""
GigPulse Sentinel Workers API
Worker profile and trust score management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Worker, get_db
from backend.models.schemas import (
    WorkerProfile,
    WorkerUpdateRequest,
    TrustScoreResponse,
    MessageResponse,
    EarningsDNAResponse,
    EarningsDNASlot,
    NotificationListResponse,
    NotificationItem,
    MarkReadResponse,
    UnreadCountResponse,
)
from backend.middleware.auth_middleware import get_current_user
from backend.services.trust_score import TrustScoreService
from backend.services.notification_service import NotificationService
from backend.ml.earnings_dna import EarningsDNA
from sqlalchemy import select

router = APIRouter(prefix="/workers", tags=["Workers"])


@router.get("/profile", response_model=WorkerProfile)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current worker's profile."""
    result = await db.execute(select(Worker).where(Worker.id == current_user["worker_id"]))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return WorkerProfile.model_validate(worker)


@router.put("/profile", response_model=MessageResponse)
async def update_profile(
    request: WorkerUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update worker profile."""
    result = await db.execute(select(Worker).where(Worker.id == current_user["worker_id"]))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    if request.name:
        worker.name = request.name
    if request.email is not None:
        worker.email = request.email.strip() or None
    if request.zone_code:
        worker.primary_zone_code = request.zone_code
    await db.flush()

    return MessageResponse(message="Profile updated successfully")


@router.get("/trust-score", response_model=TrustScoreResponse)
async def get_trust_score(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get worker's current trust score with breakdown."""
    trust_data = await TrustScoreService.calculate_trust_score(db, current_user["worker_id"])
    return TrustScoreResponse(
        worker_id=trust_data["worker_id"],
        trust_score=trust_data["trust_score"],
        is_verified_partner=trust_data["is_verified_partner"],
        clean_claims=trust_data["clean_claims"],
        total_claims=trust_data["total_claims"],
        fraud_strikes=trust_data["fraud_strikes"],
        account_status=trust_data["account_status"],
        badge=trust_data["badge"],
    )


@router.get("/earnings-dna")
async def get_earnings_dna(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get worker's Earnings DNA profile."""
    profile = EarningsDNA.build_profile(current_user["worker_id"])
    return profile


@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get worker's recent notifications (durable)."""
    items = await NotificationService.get_notifications(db, current_user["worker_id"], limit=limit)
    return NotificationListResponse(notifications=[NotificationItem(**n) for n in items])


@router.post("/notifications/{notification_id}/read", response_model=MarkReadResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    await NotificationService.mark_read(db, current_user["worker_id"], notification_id)
    return MarkReadResponse(success=True)


@router.post("/notifications/read-all", response_model=MarkReadResponse)
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all worker notifications as read."""
    await NotificationService.mark_all_read(db, current_user["worker_id"])
    return MarkReadResponse(success=True)


@router.get("/notifications/unread-count", response_model=UnreadCountResponse)
async def get_unread_notifications_count(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get worker's unread notification count (for UI badges)."""
    count = await NotificationService.get_unread_count(db, current_user["worker_id"])
    return UnreadCountResponse(unread_count=count)
