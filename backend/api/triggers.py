"""
LaborGuard Triggers API
Parametric trigger status and history
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Trigger, Worker, get_db
from backend.models.schemas import TriggerStatus, TriggerStatusResponse
from backend.middleware.auth_middleware import get_current_user
from backend.services.trigger_monitor import TriggerMonitor

router = APIRouter(prefix="/triggers", tags=["Triggers"])


@router.get("/status", response_model=TriggerStatusResponse)
async def get_trigger_status(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get real-time trigger status for the worker's zone."""
    # Get worker's zone
    result = await db.execute(
        select(Worker).where(Worker.id == current_user["worker_id"])
    )
    worker = result.scalar_one_or_none()
    zone_code = worker.primary_zone_code if worker else "CHN-VEL-4B"

    # Check triggers
    trigger_data = await TriggerMonitor.check_triggers(db, zone_code)

    # Get active triggers from DB
    active = await TriggerMonitor.get_active_triggers(db, zone_code)

    return TriggerStatusResponse(
        zone_code=zone_code,
        active_triggers=[TriggerStatus.model_validate(t) for t in active],
        weather_current=trigger_data.get("weather"),
        aqi_current=trigger_data.get("aqi"),
        platform_status=trigger_data.get("platform"),
    )


@router.get("/history")
async def get_trigger_history(
    zone_code: str = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get trigger event history."""
    query = select(Trigger).order_by(Trigger.created_at.desc()).limit(limit)

    if zone_code:
        query = query.where(Trigger.zone_code == zone_code)

    result = await db.execute(query)
    triggers = result.scalars().all()

    return {
        "triggers": [TriggerStatus.model_validate(t) for t in triggers],
        "total": len(triggers),
    }


@router.post("/simulate/{zone_code}/{trigger_type}")
async def simulate_trigger(
    zone_code: str,
    trigger_type: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Simulate a trigger event for demo purposes.
    Creates a real trigger in the database.
    """
    values = {
        "HEAVY_RAIN": 95.5,
        "FLOOD": 1.0,
        "HEAT": 44.5,
        "AQI": 435,
        "ORDER_SUSPENSION": 3.5,
    }

    value = values.get(trigger_type)
    if value is None:
        raise HTTPException(status_code=400, detail=f"Unknown trigger type: {trigger_type}")

    trigger = await TriggerMonitor.fire_trigger(
        db,
        zone_code=zone_code,
        trigger_type=trigger_type,
        value=value,
        sources_agreeing=3,
    )

    return {
        "message": f"Trigger {trigger_type} fired for zone {zone_code}",
        "trigger_id": trigger.id,
        "severity": trigger.severity,
        "auto_approved": trigger.auto_approved,
    }
