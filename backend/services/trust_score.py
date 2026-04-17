"""
GigPulse Sentinel Trust Score Service
Worker trust score computation & management
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Worker, Claim
from backend.services.notification_service import NotificationService


class TrustScoreService:
    BASE_SCORE = 50.0
    MAX_SCORE = 100.0
    VERIFIED_PARTNER_THRESHOLD = 80.0
    CLEAN_CLAIM_BONUS = 2.0
    AMBER_PENALTY = -1.0
    RED_PENALTY = -5.0
    FRAUD_STRIKE_PENALTY = -15.0
    APPEAL_WIN_BONUS = 3.0
    WEEKLY_TENURE_BONUS = 0.5

    @staticmethod
    async def calculate_trust_score(db: AsyncSession, worker_id: str) -> dict:
        result = await db.execute(select(Worker).where(Worker.id == worker_id))
        worker = result.scalar_one_or_none()
        if not worker:
            raise ValueError("Worker not found")

        score = TrustScoreService.BASE_SCORE

        claims_result = await db.execute(select(Claim).where(Claim.worker_id == worker_id))
        claims = list(claims_result.scalars().all())

        clean_claims = amber_claims = red_claims = appeal_wins = 0
        total_claims = len(claims)

        for claim in claims:
            if claim.fraud_tier == "GREEN" and claim.status in ("APPROVED", "PAID"):
                clean_claims += 1
                score += TrustScoreService.CLEAN_CLAIM_BONUS
            elif claim.fraud_tier == "AMBER":
                amber_claims += 1
                score += TrustScoreService.AMBER_PENALTY
            elif claim.fraud_tier == "RED":
                red_claims += 1
                score += TrustScoreService.RED_PENALTY
            if claim.appeal_status == "APPROVED":
                appeal_wins += 1
                score += TrustScoreService.APPEAL_WIN_BONUS

        score += worker.fraud_strikes * TrustScoreService.FRAUD_STRIKE_PENALTY
        tenure_bonus = min(worker.tenure_weeks * TrustScoreService.WEEKLY_TENURE_BONUS, 10.0)
        score += tenure_bonus
        score = max(0, min(TrustScoreService.MAX_SCORE, score))

        is_verified = score >= TrustScoreService.VERIFIED_PARTNER_THRESHOLD
        badge = "Verified Partner ⭐" if is_verified else ("Trusted Worker" if score >= 60 else ("Standard" if score >= 40 else "Under Review"))

        worker.trust_score = score
        worker.is_verified_partner = is_verified
        await db.flush()

        return {
            "worker_id": worker_id, "trust_score": round(score, 1),
            "is_verified_partner": is_verified, "badge": badge,
            "clean_claims": clean_claims, "amber_claims": amber_claims,
            "red_claims": red_claims, "appeal_wins": appeal_wins,
            "total_claims": total_claims, "fraud_strikes": worker.fraud_strikes,
            "tenure_weeks": worker.tenure_weeks, "tenure_bonus": round(tenure_bonus, 1),
            "account_status": worker.account_status,
            "breakdown": {
                "base": TrustScoreService.BASE_SCORE,
                "clean_claims_bonus": clean_claims * TrustScoreService.CLEAN_CLAIM_BONUS,
                "amber_penalty": amber_claims * TrustScoreService.AMBER_PENALTY,
                "red_penalty": red_claims * TrustScoreService.RED_PENALTY,
                "fraud_strike_penalty": worker.fraud_strikes * TrustScoreService.FRAUD_STRIKE_PENALTY,
                "tenure_bonus": tenure_bonus,
                "appeal_bonus": appeal_wins * TrustScoreService.APPEAL_WIN_BONUS,
                "final": round(score, 1),
            },
        }

    @staticmethod
    async def apply_strike(db: AsyncSession, worker_id: str, reason: str) -> dict:
        result = await db.execute(select(Worker).where(Worker.id == worker_id))
        worker = result.scalar_one_or_none()
        if not worker:
            raise ValueError("Worker not found")

        worker.fraud_strikes += 1
        action_taken = ""
        if worker.fraud_strikes == 1:
            action_taken = "Warning notification sent. No penalty."
        elif worker.fraud_strikes == 2:
            action_taken = "Premium increases next week."
        elif worker.fraud_strikes >= 3:
            worker.account_status = "SUSPENDED"
            action_taken = "Account suspended. Legal report filed."

        await db.flush()

        # Notify worker (inbox + email)
        await NotificationService.send_fraud_warning(db, worker_id, worker.fraud_strikes)
        return {
            "worker_id": worker_id, "fraud_strikes": worker.fraud_strikes,
            "action_taken": action_taken, "account_status": worker.account_status,
            "reason": reason,
        }
