"""
GigPulse Sentinel AI Agents API
FastAPI routes for all 7 AI agents powered by Cerebras Llama 3.1-8B + LangGraph
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Worker, Claim, Policy, Trigger, Zone, get_db
from backend.middleware.auth_middleware import get_current_user, require_admin
from backend.agents.fraud_investigator import FraudInvestigatorAgent
from backend.agents.trigger_validator import TriggerValidatorAgent
from backend.agents.earnings_intelligence import EarningsIntelligenceAgent
from backend.agents.risk_pricing import RiskPricingAgent
from backend.agents.ring_detective import RingDetectiveAgent
from backend.agents.worker_assistant import WorkerAssistantAgent
from backend.agents.appeal_handler import AppealHandlerAgent

router = APIRouter(prefix="/agents", tags=["AI Agents"])


# ─── Request Models ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(description="Worker's question in natural language")

class AppealAgentRequest(BaseModel):
    appeal_reason: str = Field(default="I believe my claim was genuine")

class InvestigateRequest(BaseModel):
    location_data: dict = Field(default=None, description="Optional GPS/location data override")
    device_data: dict = Field(default=None, description="Optional device data override")
    platform_data: dict = Field(default=None, description="Optional platform data override")


# ─── Agent 1: Fraud Investigation ────────────────────────────────────────────

@router.post("/investigate/{claim_id}")
async def investigate_claim(
    claim_id: str,
    request: InvestigateRequest = None,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Run AI fraud investigation on a specific claim."""
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    req = request or InvestigateRequest()
    investigation = await FraudInvestigatorAgent.investigate(
        worker_id=claim.worker_id,
        claim_type=claim.claim_type,
        zone_code=claim.zone_code,
        disruption_hours=claim.disruption_hours,
        location_data=req.location_data,
        device_data=req.device_data,
        platform_data=req.platform_data,
    )

    return {"agent": "FraudInvestigator", "claim_id": claim_id, "investigation": investigation}


# ─── Agent 2: Trigger Validation ─────────────────────────────────────────────

@router.post("/validate-trigger/{trigger_id}")
async def validate_trigger(
    trigger_id: str,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """AI validates a trigger event by cross-checking sources."""
    result = await db.execute(select(Trigger).where(Trigger.id == trigger_id))
    trigger = result.scalar_one_or_none()
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    # Get zone data
    zone_data = {}
    zone_result = await db.execute(select(Zone).where(Zone.id == trigger.zone_id))
    zone = zone_result.scalar_one_or_none()
    if zone:
        zone_data = {
            "city": zone.city, "area_name": zone.area_name,
            "flood_risk_score": zone.flood_risk_score,
            "heat_risk_score": zone.heat_risk_score,
            "aqi_risk_score": zone.aqi_risk_score,
        }

    trigger_data = {
        "trigger_type": trigger.trigger_type, "zone_code": trigger.zone_code,
        "severity": trigger.severity, "threshold_value": trigger.threshold_value,
        "threshold_limit": trigger.threshold_limit,
        "source_primary": trigger.source_primary,
        "source_secondary": trigger.source_secondary,
        "source_tertiary": trigger.source_tertiary,
        "sources_agreeing": trigger.sources_agreeing,
        "auto_approved": trigger.auto_approved,
    }

    validation = await TriggerValidatorAgent.validate(trigger_data, zone_data)
    return {"agent": "TriggerValidator", "trigger_id": trigger_id, "validation": validation}


# ─── Agent 3: Earnings Intelligence ──────────────────────────────────────────

@router.get("/earnings-insight/{worker_id}")
async def earnings_insight(
    worker_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI-powered earnings analysis with dynamic payout recommendation."""
    result = await db.execute(select(Worker).where(Worker.id == worker_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker_data = {
        "avg_daily_earnings": worker.avg_daily_earnings,
        "avg_weekly_earnings": worker.avg_weekly_earnings,
        "tenure_weeks": worker.tenure_weeks,
        "primary_zone_code": worker.primary_zone_code,
        "platform": worker.platform or "zomato",
    }

    insight = await EarningsIntelligenceAgent.analyze(
        worker_data=worker_data,
        original_payout=worker.avg_daily_earnings * 0.4 * 1.5,
        disruption_hours=4.0,
    )

    return {"agent": "EarningsIntelligence", "worker_id": worker_id, "insight": insight}


# ─── Agent 4: Risk Pricing ───────────────────────────────────────────────────

@router.get("/price-risk/{worker_id}")
async def price_risk(
    worker_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI dynamic premium recommendation based on live conditions."""
    result = await db.execute(select(Worker).where(Worker.id == worker_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    # Get zone data
    zone_data = {"zone_code": worker.primary_zone_code or "CHN-VEL-4B"}
    if worker.zone_id:
        zone_result = await db.execute(select(Zone).where(Zone.id == worker.zone_id))
        zone = zone_result.scalar_one_or_none()
        if zone:
            zone_data = {
                "zone_code": zone.zone_code, "city": zone.city,
                "flood_risk_score": zone.flood_risk_score,
                "heat_risk_score": zone.heat_risk_score,
                "aqi_risk_score": zone.aqi_risk_score,
                "strike_frequency_yearly": zone.strike_frequency_yearly,
            }

    worker_data = {
        "avg_weekly_earnings": worker.avg_weekly_earnings,
        "tenure_weeks": worker.tenure_weeks,
        "trust_score": worker.trust_score,
    }

    # Get current policy
    policy_result = await db.execute(
        select(Policy).where(Policy.worker_id == worker_id, Policy.status == "ACTIVE")
        .order_by(Policy.created_at.desc()).limit(1)
    )
    policy = policy_result.scalar_one_or_none()
    current_plan = policy.plan_tier if policy else "STANDARD"
    current_premium = policy.premium_amount if policy else 45

    pricing = await RiskPricingAgent.analyze(worker_data, zone_data, current_plan, current_premium)
    return {"agent": "RiskPricing", "worker_id": worker_id, "pricing": pricing}


# ─── Agent 5: Ring Detective ─────────────────────────────────────────────────

@router.post("/investigate-ring")
async def investigate_ring(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """AI investigates detected fraud rings with detailed evidence analysis."""
    from backend.services.ring_detector import RingDetector
    detected = await RingDetector.detect_rings(db)
    investigation = await RingDetectiveAgent.investigate(detected)
    return {"agent": "RingDetective", "investigation": investigation}


# ─── Agent 6: Worker Chat ────────────────────────────────────────────────────

@router.post("/chat")
async def worker_chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI chatbot for workers — answers questions in plain language."""
    # Gather context
    worker_result = await db.execute(select(Worker).where(Worker.id == current_user["worker_id"]))
    worker = worker_result.scalar_one_or_none()

    worker_data = {}
    claim_data = {}
    policy_data = {}

    if worker:
        worker_data = {
            "name": worker.name, "platform": worker.platform or "zomato",
            "primary_zone_code": worker.primary_zone_code,
            "trust_score": worker.trust_score, "account_status": worker.account_status,
            "avg_daily_earnings": worker.avg_daily_earnings,
        }

        # Get latest claim
        claim_result = await db.execute(
            select(Claim).where(Claim.worker_id == worker.id)
            .order_by(Claim.created_at.desc()).limit(1)
        )
        claim = claim_result.scalar_one_or_none()
        if claim:
            claim_data = {
                "claim_type": claim.claim_type, "status": claim.status,
                "calculated_payout": claim.calculated_payout,
                "actual_payout": claim.actual_payout or 0,
            }

        # Get active policy
        policy_result = await db.execute(
            select(Policy).where(Policy.worker_id == worker.id, Policy.status == "ACTIVE")
            .order_by(Policy.created_at.desc()).limit(1)
        )
        policy = policy_result.scalar_one_or_none()
        if policy:
            policy_data = {
                "plan_tier": policy.plan_tier, "premium_amount": policy.premium_amount,
                "coverage_amount": policy.coverage_amount,
            }

    response = await WorkerAssistantAgent.chat(
        question=request.message,
        worker_data=worker_data,
        claim_data=claim_data,
        policy_data=policy_data,
    )

    return {"agent": "WorkerAssistant", "response": response}


# ─── Agent 7: Appeal Handler ─────────────────────────────────────────────────

@router.post("/handle-appeal/{claim_id}")
async def handle_appeal(
    claim_id: str,
    request: AppealAgentRequest,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """AI-powered appeal resolution with evidence re-evaluation."""
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Get worker data
    worker_result = await db.execute(select(Worker).where(Worker.id == claim.worker_id))
    worker = worker_result.scalar_one_or_none()

    claim_data = {
        "claim_type": claim.claim_type, "zone_code": claim.zone_code,
        "disruption_hours": claim.disruption_hours,
        "calculated_payout": claim.calculated_payout,
        "fraud_score": claim.fraud_score, "fraud_tier": claim.fraud_tier,
        "status": claim.status,
    }

    worker_data = {}
    if worker:
        worker_data = {
            "tenure_weeks": worker.tenure_weeks,
            "trust_score": worker.trust_score,
            "fraud_strikes": worker.fraud_strikes,
        }

    decision = await AppealHandlerAgent.handle(
        claim_data=claim_data,
        appeal_reason=request.appeal_reason,
        worker_data=worker_data,
    )

    return {"agent": "AppealHandler", "claim_id": claim_id, "decision": decision}
