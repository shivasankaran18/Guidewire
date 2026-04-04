"""
LaborGuard Notification Service
Push notification dispatch for workers
"""

from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class Notification:
    title: str
    message: str
    type: str  # INFO, WARNING, ALERT, PAYOUT, COVERAGE
    worker_id: str
    data: dict = None
    created_at: str = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.data:
            self.data = {}


class NotificationService:
    """Notification dispatch service for LaborGuard."""

    # In-memory notification store (demo mode)
    _notifications: list[Notification] = []

    @staticmethod
    def send_coverage_nudge(
        worker_id: str,
        zone_risk_percent: float,
        coverage_amount: float,
        premium_amount: float,
    ) -> Notification:
        """Monday coverage nudge notification."""
        notif = Notification(
            title="⚠️ Weekly Coverage Reminder",
            message=(
                f"High flood risk this week in your zone ({zone_risk_percent:.0f}%). "
                f"Your coverage: ₹{coverage_amount:,.0f}. "
                f"Premium: ₹{premium_amount:,.0f}. "
                "Tap to renew."
            ),
            type="COVERAGE",
            worker_id=worker_id,
            data={
                "action": "RENEW_COVERAGE",
                "risk_percent": zone_risk_percent,
                "coverage": coverage_amount,
                "premium": premium_amount,
            },
        )
        NotificationService._notifications.append(notif)
        return notif

    @staticmethod
    def send_payout_notification(
        worker_id: str,
        amount: float,
        trigger_type: str,
        confidence: float,
    ) -> Notification:
        """Instant payout notification."""
        trigger_names = {
            "HEAVY_RAIN": "heavy rainfall",
            "FLOOD": "flooding",
            "HEAT": "severe heat",
            "AQI": "hazardous air quality",
            "ORDER_SUSPENSION": "order suspension",
        }
        notif = Notification(
            title="💰 Payout Processed!",
            message=(
                f"₹{amount:,.0f} sent to your UPI due to {trigger_names.get(trigger_type, trigger_type)}. "
                f"Your claim was verified with {confidence:.0f}% confidence based on weather data, "
                "your zone history, and platform activity."
            ),
            type="PAYOUT",
            worker_id=worker_id,
            data={
                "amount": amount,
                "trigger": trigger_type,
                "confidence": confidence,
            },
        )
        NotificationService._notifications.append(notif)
        return notif

    @staticmethod
    def send_claim_update(
        worker_id: str,
        claim_id: str,
        status: str,
        message: str = None,
    ) -> Notification:
        """Claim status update notification."""
        status_emojis = {
            "APPROVED": "✅",
            "REJECTED": "❌",
            "PENDING": "⏳",
            "APPEALED": "📋",
            "PAID": "💰",
        }
        notif = Notification(
            title=f"{status_emojis.get(status, '📢')} Claim {status.title()}",
            message=message or f"Your claim has been {status.lower()}.",
            type="ALERT",
            worker_id=worker_id,
            data={
                "claim_id": claim_id,
                "status": status,
            },
        )
        NotificationService._notifications.append(notif)
        return notif

    @staticmethod
    def send_fraud_warning(
        worker_id: str,
        strike_number: int,
    ) -> Notification:
        """Fraud strike warning notification."""
        messages = {
            1: "A suspicious activity was flagged on your account. This is a warning — no penalty applied. Please ensure your GPS and device settings are correct.",
            2: "A second suspicious activity was confirmed. Your premium may increase next week. Contact support if you believe this is an error.",
            3: "Multiple confirmed fraud incidents detected. Your account has been suspended pending review. A legal report has been filed.",
        }
        notif = Notification(
            title=f"⚠️ Account Warning (Strike {strike_number}/3)",
            message=messages.get(strike_number, "Account activity flagged."),
            type="WARNING",
            worker_id=worker_id,
            data={
                "strike_number": strike_number,
                "action": "SUSPENDED" if strike_number >= 3 else "WARNING",
            },
        )
        NotificationService._notifications.append(notif)
        return notif

    @staticmethod
    def get_notifications(worker_id: str, limit: int = 20) -> list[dict]:
        """Get recent notifications for a worker."""
        worker_notifs = [
            {
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "data": n.data,
                "created_at": n.created_at,
            }
            for n in reversed(NotificationService._notifications)
            if n.worker_id == worker_id
        ]
        return worker_notifs[:limit]
