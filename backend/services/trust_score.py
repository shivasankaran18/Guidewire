"""
LaborGuard Trust Score Service
Worker trust score computation & management
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Worker, Claim


class TrustScoreService:
    """
    Worker trust score management.
    Trust Score (0-100) based on clean claim history.
    """

    # Trust score config
    BASE_SCORE = 50.0
    MAX_SCORE = 100.0
    VERIFIED_PARTNER_THRESHOLD = 80.0
    PROBATION_WEEKS = 2

    # Score adjustments
    CLEAN_CLAIM_BONUS = 2.0       # +2 per clean (Green) claim
    AMBER_PENALTY = -1.0          # -1 per Amber claim
    RED_PENALTY = -5.0            # -5 per Red-flagged claim
    FRAUD_STRIKE_PENALTY = -15.0  # -15 per confirmed fraud strike
    APPEAL_WIN_BONUS = 3.0        # +3 when appeal succeeds (false positive recovery)
    WEEKLY_TENURE_BONUS = 0.5     # +0.5 per week of tenure (max 10)

    @staticmethod
    async def calculate_trust_score(
        db: AsyncSession,
        worker_id: str,
    ) -> dict:
        """Calculate current trust score for a worker."""
        result = await db.execute(select(Worker).where(Worker.id == worker_id))
        worker = result.scalar_one_or_none()
        if not worker:
            raise ValueError("Worker not found")

        # Start with base score
        score = TrustScoreService.BASE_SCORE

        # Get claim statistics
        claims_result = await db.execute(
            select(Claim).where(Claim.worker_id == worker_id)
        )
        claims = list(claims_result.scalars().all())

        clean_claims = 0
        amber_claims = 0
        red_claims = 0
        appeal_wins = 0
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

        # Fraud strikes
        score += worker.fraud_strikes * TrustScoreService.FRAUD_STRIKE_PENALTY

        # Tenure bonus (capped at 10 points)
        tenure_bonus = min(
            worker.tenure_weeks * TrustScoreService.WEEKLY_TENURE_BONUS,
            10.0
        )
        score += tenure_bonus

        # Clamp score
        score = max(0, min(TrustScoreService.MAX_SCORE, score))

        # Determine badge
        is_verified = score >= TrustScoreService.VERIFIED_PARTNER_THRESHOLD
        badge = None
        if is_verified:
            badge = "Verified Partner ⭐"
        elif score >= 60:
            badge = "Trusted Worker"
        elif score >= 40:
            badge = "Standard"
        else:
            badge = "Under Review"

        # Update worker
        worker.trust_score = score
        worker.is_verified_partner = is_verified
        await db.flush()

        return {
            "worker_id": worker_id,
            "trust_score": round(score, 1),
            "is_verified_partner": is_verified,
            "badge": badge,
            "clean_claims": clean_claims,
            "amber_claims": amber_claims,
            "red_claims": red_claims,
            "appeal_wins": appeal_wins,
            "total_claims": total_claims,
            "fraud_strikes": worker.fraud_strikes,
            "tenure_weeks": worker.tenure_weeks,
            "tenure_bonus": round(tenure_bonus, 1),
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
    async def apply_strike(
        db: AsyncSession,
        worker_id: str,
        reason: str,
    ) -> dict:
        """Apply a fraud strike to a worker."""
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

        return {
            "worker_id": worker_id,
            "fraud_strikes": worker.fraud_strikes,
            "action_taken": action_taken,
            "account_status": worker.account_status,
            "reason": reason,
        }
