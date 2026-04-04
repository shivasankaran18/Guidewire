"""
LaborGuard Premium Engine Service
XGBoost-based dynamic weekly premium calculation
Sub-zone precision: priced at 500m polygon level
"""

import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Worker, Policy, Zone
from backend.services.zone_engine import ZoneEngine


# Plan tier configurations
PLAN_TIERS = {
    "BASIC": {
        "name": "Basic Shield",
        "coverage_multiplier": 1.0,
        "premium_multiplier": 1.0,
        "description": "Essential income protection for disruption events",
        "features": [
            "Coverage for heavy rainfall & floods",
            "Basic payout within 2 hours",
            "Up to 1x weekly earnings coverage",
        ],
    },
    "STANDARD": {
        "name": "Standard Shield",
        "coverage_multiplier": 1.5,
        "premium_multiplier": 1.4,
        "description": "Enhanced protection with faster payouts",
        "features": [
            "All Basic features",
            "Coverage for heat waves & AQI emergencies",
            "Instant payout for Green-tier claims",
            "Up to 1.5x weekly earnings coverage",
            "Priority customer support",
        ],
    },
    "PREMIUM": {
        "name": "Premium Shield",
        "coverage_multiplier": 2.0,
        "premium_multiplier": 1.8,
        "description": "Maximum protection with highest payouts",
        "features": [
            "All Standard features",
            "Coverage for platform order suspensions",
            "Instant payout for Green & Amber claims",
            "Up to 2x weekly earnings coverage",
            "₹50 goodwill credit on false positives",
            "Verified Partner fast-track",
        ],
    },
}

# Premium range bounds
MIN_PREMIUM = 29.0  # ₹29/week
MAX_PREMIUM = 75.0  # ₹75/week


class PremiumEngine:
    """Dynamic weekly premium calculator using XGBoost-style risk scoring."""

    @staticmethod
    async def calculate_premium(
        db: AsyncSession,
        worker_id: str,
        plan_tier: str = "BASIC",
    ) -> dict:
        """
        Calculate personalized weekly premium for a worker.
        Uses zone risk factors, worker history, and plan tier.
        """
        # Get worker
        result = await db.execute(select(Worker).where(Worker.id == worker_id))
        worker = result.scalar_one_or_none()
        if not worker:
            raise ValueError("Worker not found")

        # Get zone risk factors
        zone_risk = await ZoneEngine.get_zone_risk_for_premium(
            db, worker.primary_zone_code or "CHN-VEL-4B"
        )

        # Calculate base premium from risk factors
        risk_features = {
            "flood_risk_3yr": zone_risk.get("flood_risk_3yr", 50),
            "heat_risk_forecast": zone_risk.get("heat_risk", 50),
            "aqi_forecast": zone_risk.get("aqi_risk", 50),
            "strike_frequency": zone_risk.get("strike_frequency", 1.0),
            "avg_weekly_earnings": worker.avg_weekly_earnings or 5000,
            "tenure_weeks": worker.tenure_weeks or 0,
            "past_claims_ratio": 0,  # Would be calculated from claims history
        }

        # XGBoost-style risk scoring (simplified for demo)
        base_premium = PremiumEngine._compute_base_premium(risk_features)

        # Apply plan multiplier
        tier_config = PLAN_TIERS.get(plan_tier, PLAN_TIERS["BASIC"])
        final_premium = base_premium * tier_config["premium_multiplier"]

        # Clamp to range
        final_premium = max(MIN_PREMIUM, min(MAX_PREMIUM * tier_config["premium_multiplier"], final_premium))
        final_premium = round(final_premium, 0)

        # Calculate coverage amount
        weekly_earnings = worker.avg_weekly_earnings or 5000
        coverage_amount = weekly_earnings * tier_config["coverage_multiplier"]

        return {
            "worker_id": worker_id,
            "plan_tier": plan_tier,
            "plan_name": tier_config["name"],
            "premium_amount": final_premium,
            "coverage_amount": round(coverage_amount, 0),
            "coverage_multiplier": tier_config["coverage_multiplier"],
            "risk_factors": risk_features,
            "zone_info": {
                "zone_code": zone_risk.get("zone_code", "Unknown"),
                "city": zone_risk.get("city", "Unknown"),
                "area_name": zone_risk.get("area_name", "Unknown"),
                "risk_level": zone_risk.get("overall_risk_level", "MEDIUM"),
            },
            "breakdown": {
                "base_premium": round(base_premium, 2),
                "tier_multiplier": tier_config["premium_multiplier"],
                "final_premium": final_premium,
            },
        }

    @staticmethod
    def _compute_base_premium(features: dict) -> float:
        """
        Compute base premium using weighted risk scoring.
        In production, this would be an XGBoost regression model.
        """
        # Feature weights (from XGBoost feature importance)
        weights = {
            "flood_risk_3yr": 0.28,
            "heat_risk_forecast": 0.12,
            "aqi_forecast": 0.12,
            "strike_frequency": 0.18,
            "avg_weekly_earnings": 0.15,
            "tenure_weeks": -0.08,  # Veteran discount
            "past_claims_ratio": 0.07,
        }

        # Normalize features to 0-1 range
        normalized = {
            "flood_risk_3yr": features["flood_risk_3yr"] / 100,
            "heat_risk_forecast": features["heat_risk_forecast"] / 100,
            "aqi_forecast": features["aqi_forecast"] / 100,
            "strike_frequency": min(features["strike_frequency"] / 5, 1),
            "avg_weekly_earnings": min(features["avg_weekly_earnings"] / 10000, 1),
            "tenure_weeks": min(features["tenure_weeks"] / 52, 1),
            "past_claims_ratio": features["past_claims_ratio"],
        }

        # Weighted sum
        risk_score = sum(
            normalized[key] * weights[key] for key in weights
        )

        # Map risk_score (roughly 0-0.5) to premium range (29-75)
        premium = MIN_PREMIUM + (risk_score * (MAX_PREMIUM - MIN_PREMIUM) * 2.5)
        return max(MIN_PREMIUM, min(MAX_PREMIUM, premium))

    @staticmethod
    async def create_policy(
        db: AsyncSession,
        worker_id: str,
        plan_tier: str,
        payment_reference: str = None,
    ) -> Policy:
        """Create a weekly coverage policy."""
        premium_calc = await PremiumEngine.calculate_premium(db, worker_id, plan_tier)

        now = datetime.now(timezone.utc)
        # Week starts now, ends Sunday
        days_until_sunday = 6 - now.weekday()
        if days_until_sunday <= 0:
            days_until_sunday = 7
        week_end = now + timedelta(days=days_until_sunday)

        tier_config = PLAN_TIERS[plan_tier]

        policy = Policy(
            id=str(uuid.uuid4()),
            worker_id=worker_id,
            plan_tier=plan_tier,
            premium_amount=premium_calc["premium_amount"],
            coverage_amount=premium_calc["coverage_amount"],
            coverage_multiplier=tier_config["coverage_multiplier"],
            week_start=now.strftime("%Y-%m-%d"),
            week_end=week_end.strftime("%Y-%m-%d"),
            status="ACTIVE",
            payment_reference=payment_reference or f"UPI_{uuid.uuid4().hex[:12].upper()}",
            payment_status="PAID",
            risk_factors=premium_calc["risk_factors"],
        )

        db.add(policy)
        await db.flush()
        return policy

    @staticmethod
    def get_plan_tiers() -> list[dict]:
        """Get all available plan tiers."""
        return [
            {
                "tier": tier,
                "name": config["name"],
                "premium_range": f"₹{int(MIN_PREMIUM * config['premium_multiplier'])}–₹{int(MAX_PREMIUM * config['premium_multiplier'])}",
                "coverage_multiplier": config["coverage_multiplier"],
                "description": config["description"],
                "features": config["features"],
            }
            for tier, config in PLAN_TIERS.items()
        ]
