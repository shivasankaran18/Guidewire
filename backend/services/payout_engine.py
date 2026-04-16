"""
GigPulse Sentinel Payout Engine Service
Earnings DNA-based payout calculation
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Claim, Policy, Worker, Payout, EarningsPattern

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class PayoutEngine:
    @staticmethod
    async def calculate_payout(db: AsyncSession, worker_id: str, policy_id: str,
                                trigger_type: str, disruption_hours: float,
                                disruption_day: int = None, disruption_hour: int = None) -> dict:
        result = await db.execute(select(Worker).where(Worker.id == worker_id))
        worker = result.scalar_one_or_none()
        if not worker:
            raise ValueError("Worker not found")

        result = await db.execute(select(Policy).where(Policy.id == policy_id))
        policy = result.scalar_one_or_none()
        if not policy:
            raise ValueError("No active policy found")

        now = datetime.now(timezone.utc)
        day = disruption_day if disruption_day is not None else now.weekday()
        hour = disruption_hour if disruption_hour is not None else now.hour

        earnings_for_slot = await PayoutEngine._get_earnings_for_slot(db, worker_id, day, hour)

        working_hours = 10.0
        payout = earnings_for_slot * (disruption_hours / working_hours) * policy.coverage_multiplier
        payout_cap = 2 * policy.premium_amount * policy.coverage_multiplier
        actual_payout = min(payout, payout_cap)

        return {
            "worker_id": worker_id, "policy_id": policy_id, "trigger_type": trigger_type,
            "earnings_for_slot": round(earnings_for_slot, 2),
            "disruption_day": DAY_NAMES[day], "disruption_hour": hour,
            "disruption_hours": disruption_hours, "working_hours": working_hours,
            "coverage_multiplier": policy.coverage_multiplier,
            "calculated_payout": round(payout, 2), "payout_cap": round(payout_cap, 2),
            "actual_payout": round(actual_payout, 2), "is_capped": payout > payout_cap,
            "breakdown": {
                "formula": "Earnings × (Disruption/Working Hours) × Coverage Multiplier",
                "earnings": round(earnings_for_slot, 2),
                "ratio": round(disruption_hours / working_hours, 2),
                "multiplier": policy.coverage_multiplier,
                "pre_cap": round(payout, 2), "cap": round(payout_cap, 2),
            },
        }

    @staticmethod
    async def _get_earnings_for_slot(db: AsyncSession, worker_id: str, day_of_week: int, hour_slot: int) -> float:
        result = await db.execute(
            select(EarningsPattern).where(
                EarningsPattern.worker_id == worker_id,
                EarningsPattern.day_of_week == day_of_week,
                EarningsPattern.hour_slot == hour_slot,
            )
        )
        pattern = result.scalar_one_or_none()
        if pattern:
            return pattern.avg_earnings

        result = await db.execute(select(Worker).where(Worker.id == worker_id))
        worker = result.scalar_one_or_none()
        if worker:
            return worker.avg_daily_earnings or 700
        return 700

    @staticmethod
    async def process_payout(db: AsyncSession, claim_id: str, amount: float, goodwill_credit: float = 0) -> Payout:
        result = await db.execute(select(Claim).where(Claim.id == claim_id))
        claim = result.scalar_one_or_none()
        if not claim:
            raise ValueError("Claim not found")

        payout = Payout(
            id=str(uuid.uuid4()), claim_id=claim_id, worker_id=claim.worker_id,
            amount=amount, upi_reference=f"UPI_{uuid.uuid4().hex[:12].upper()}",
            payment_method="UPI", payment_status="COMPLETED",
            goodwill_credit=goodwill_credit, paid_at=datetime.now(timezone.utc),
        )
        db.add(payout)

        claim.actual_payout = amount
        claim.status = "PAID"
        claim.paid_at = datetime.now(timezone.utc)
        await db.flush()
        return payout

    @staticmethod
    def generate_earnings_dna(worker_id: str) -> list[dict]:
        import random
        patterns = []
        for day in range(7):
            for hour in range(24):
                if 6 <= hour <= 8:
                    base = random.uniform(40, 60)
                elif 11 <= hour <= 14:
                    base = random.uniform(80, 120)
                elif 17 <= hour <= 21:
                    base = random.uniform(100, 150)
                elif 22 <= hour or hour <= 5:
                    base = random.uniform(0, 20)
                else:
                    base = random.uniform(30, 50)
                if day >= 5:
                    base *= 1.3
                if day == 4 and 18 <= hour <= 21:
                    base *= 1.5
                patterns.append({
                    "worker_id": worker_id, "day_of_week": day,
                    "day_name": DAY_NAMES[day], "hour_slot": hour,
                    "avg_earnings": round(base, 2), "order_count": max(0, int(base / 25)),
                })
        return patterns
