"""GigPulse Sentinel Notification Service.

Provides durable (DB-backed) notifications with optional email delivery.

Design goals:
- Persist notifications in DB (inbox).
- Track delivery attempts for EMAIL channel.
- Safe in multi-instance deployments (jobs use Postgres advisory locks).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import smtplib
from email.message import EmailMessage

from sqlalchemy import select, update, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.settings import get_settings
from backend.models.database import Notification, NotificationDelivery, Worker


settings = get_settings()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


@dataclass
class OutboxEmail:
    to: str
    subject: str
    body: str


class NotificationService:
    """Notification dispatch service for GigPulse Sentinel."""

    # ----------------------------
    # Creation
    # ----------------------------
    @staticmethod
    async def create_notification(
        db: AsyncSession,
        worker_id: str,
        *,
        title: str,
        message: str,
        type: str,
        data: dict | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
        dedupe_key: str | None = None,
        send_email: bool = True,
    ) -> Notification:
        """Create a notification and enqueue delivery channels.

        If dedupe_key is provided, this is idempotent per-worker.
        """

        if data is None:
            data = {}

        # Dedupe if needed
        if dedupe_key:
            existing = await db.execute(
                select(Notification)
                .where(Notification.worker_id == worker_id, Notification.dedupe_key == dedupe_key)
                .limit(1)
            )
            notif = existing.scalar_one_or_none()
            if notif is not None:
                return notif

        notif = Notification(
            worker_id=worker_id,
            type=type,
            title=title,
            message=message,
            data=data,
            source_type=source_type,
            source_id=source_id,
            dedupe_key=dedupe_key,
            created_at=_utcnow(),
        )
        db.add(notif)
        await db.flush()

        # INBOX delivery is effectively immediate once stored
        db.add(
            NotificationDelivery(
                notification_id=notif.id,
                channel="INBOX",
                status="SENT",
                attempts=1,
                sent_at=_utcnow(),
                created_at=_utcnow(),
            )
        )

        if send_email:
            # We enqueue EMAIL and let the scheduler process it.
            db.add(
                NotificationDelivery(
                    notification_id=notif.id,
                    channel="EMAIL",
                    status="PENDING",
                    attempts=0,
                    next_attempt_at=_utcnow(),
                    created_at=_utcnow(),
                )
            )

        await db.flush()
        return notif

    # ----------------------------
    # Convenience wrappers
    # ----------------------------
    @staticmethod
    async def send_coverage_nudge(
        db: AsyncSession,
        worker_id: str,
        zone_risk_percent: float,
        coverage_amount: float,
        premium_amount: float,
        *,
        dedupe_key: str | None = None,
    ) -> Notification:
        return await NotificationService.create_notification(
            db,
            worker_id,
            title="Weekly Coverage Reminder",
            message=(
                f"High flood risk this week in your zone ({zone_risk_percent:.0f}%). "
                f"Your coverage: ₹{coverage_amount:,.0f}. Premium: ₹{premium_amount:,.0f}. Tap to renew."
            ),
            type="COVERAGE",
            data={
                "action": "RENEW_COVERAGE",
                "risk_percent": zone_risk_percent,
                "coverage": coverage_amount,
                "premium": premium_amount,
            },
            source_type="POLICY",
            source_id=None,
            dedupe_key=dedupe_key,
            send_email=True,
        )

    @staticmethod
    async def send_payout_notification(
        db: AsyncSession,
        worker_id: str,
        amount: float,
        trigger_type: str,
        confidence: float,
        *,
        claim_id: str | None = None,
    ) -> Notification:
        trigger_names = {
            "HEAVY_RAIN": "heavy rainfall",
            "FLOOD": "flooding",
            "HEAT": "severe heat",
            "AQI": "hazardous air quality",
            "ORDER_SUSPENSION": "order suspension",
        }
        conf_pct = confidence * 100 if confidence <= 1 else confidence
        return await NotificationService.create_notification(
            db,
            worker_id,
            title="Payout Processed",
            message=(
                f"₹{amount:,.0f} sent to your UPI due to {trigger_names.get(trigger_type, trigger_type)}. "
                f"Verified with {conf_pct:.0f}% confidence."
            ),
            type="PAYOUT",
            data={"amount": amount, "trigger": trigger_type, "confidence": conf_pct, "claim_id": claim_id},
            source_type="CLAIM" if claim_id else "PAYOUT",
            source_id=claim_id,
            dedupe_key=f"payout:{claim_id}" if claim_id else None,
            send_email=True,
        )

    @staticmethod
    async def send_claim_update(
        db: AsyncSession,
        worker_id: str,
        claim_id: str,
        status: str,
        message: str | None = None,
    ) -> Notification:
        return await NotificationService.create_notification(
            db,
            worker_id,
            title=f"Claim {status.title()}",
            message=message or f"Your claim has been {status.lower()}.",
            type="ALERT",
            data={"claim_id": claim_id, "status": status},
            source_type="CLAIM",
            source_id=claim_id,
            dedupe_key=f"claim:{claim_id}:{status}",
            send_email=True,
        )

    @staticmethod
    async def send_fraud_warning(
        db: AsyncSession,
        worker_id: str,
        strike_number: int,
    ) -> Notification:
        messages = {
            1: "A suspicious activity was flagged on your account. This is a warning. Please ensure your GPS and device settings are correct.",
            2: "A second suspicious activity was confirmed. Your premium may increase next week. Contact support if you believe this is an error.",
            3: "Multiple confirmed fraud incidents detected. Your account has been suspended pending review.",
        }
        return await NotificationService.create_notification(
            db,
            worker_id,
            title=f"Account Warning (Strike {strike_number}/3)",
            message=messages.get(strike_number, "Account activity flagged."),
            type="WARNING",
            data={"strike_number": strike_number, "action": "SUSPENDED" if strike_number >= 3 else "WARNING"},
            source_type="WORKER",
            source_id=worker_id,
            dedupe_key=f"fraud_strike:{strike_number}",
            send_email=True,
        )

    # ----------------------------
    # Read APIs
    # ----------------------------
    @staticmethod
    async def get_notifications(db: AsyncSession, worker_id: str, *, limit: int = 20) -> list[dict]:
        result = await db.execute(
            select(Notification)
            .where(Notification.worker_id == worker_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        notifs = list(result.scalars().all())
        return [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "data": n.data or {},
                "created_at": _as_iso(n.created_at),
                "read_at": _as_iso(n.read_at),
            }
            for n in notifs
        ]

    @staticmethod
    async def get_unread_count(db: AsyncSession, worker_id: str) -> int:
        res = await db.execute(
            select(func.count(Notification.id)).where(
                Notification.worker_id == worker_id,
                Notification.read_at.is_(None),
            )
        )
        return int(res.scalar() or 0)

    @staticmethod
    async def mark_read(db: AsyncSession, worker_id: str, notification_id: str) -> None:
        await db.execute(
            update(Notification)
            .where(Notification.id == notification_id, Notification.worker_id == worker_id)
            .values(read_at=_utcnow())
        )
        await db.flush()

    @staticmethod
    async def mark_all_read(db: AsyncSession, worker_id: str) -> None:
        await db.execute(
            update(Notification)
            .where(Notification.worker_id == worker_id, Notification.read_at.is_(None))
            .values(read_at=_utcnow())
        )
        await db.flush()

    # ----------------------------
    # Email delivery
    # ----------------------------
    @staticmethod
    async def process_pending_email_deliveries(db: AsyncSession, *, limit: int = 50) -> dict:
        """Send pending notification emails.

        This should be called from a background job. Uses row-level selection but
        expects the caller to hold a leader/job advisory lock.
        """

        now = _utcnow()
        q = (
            select(NotificationDelivery)
            .where(
                NotificationDelivery.channel == "EMAIL",
                NotificationDelivery.status.in_(["PENDING", "FAILED"]),
                or_(
                    NotificationDelivery.next_attempt_at.is_(None),
                    NotificationDelivery.next_attempt_at <= now,
                ),
            )
            .order_by(NotificationDelivery.created_at.asc())
            .limit(limit)
        )
        result = await db.execute(q)
        deliveries = list(result.scalars().all())

        sent = failed = skipped = 0
        for d in deliveries:
            # Load notification
            notif_res = await db.execute(select(Notification).where(Notification.id == d.notification_id))
            notif = notif_res.scalar_one_or_none()
            if notif is None:
                d.status = "SKIPPED"
                d.last_error = "Notification not found"
                skipped += 1
                continue

            # Load worker email
            worker_res = await db.execute(select(Worker).where(Worker.id == notif.worker_id))
            worker = worker_res.scalar_one_or_none()
            to_addr = (worker.email.strip() if worker and worker.email else "")
            if not to_addr:
                d.status = "SKIPPED"
                d.last_error = "Worker email not set"
                skipped += 1
                continue

            try:
                d.attempts = int(d.attempts or 0) + 1
                NotificationService._send_email(
                    OutboxEmail(
                        to=to_addr,
                        subject=f"GigPulse Sentinel: {notif.title}",
                        body=NotificationService._render_email_body(notif),
                    )
                )
                d.status = "SENT"
                d.sent_at = _utcnow()
                d.last_error = None
                sent += 1
            except Exception as e:
                d.status = "FAILED"
                d.last_error = str(e)
                # backoff: 1m, 5m, 15m, 1h, 6h
                backoffs = [60, 300, 900, 3600, 21600]
                idx = min(d.attempts - 1, len(backoffs) - 1)
                d.next_attempt_at = _utcnow() + timedelta(seconds=backoffs[idx])
                failed += 1

        await db.flush()
        return {"sent": sent, "failed": failed, "skipped": skipped, "scanned": len(deliveries)}

    @staticmethod
    def _render_email_body(notif: Notification) -> str:
        data = notif.data or {}
        extra = ""
        try:
            extra = "\n\nDetails:\n" + json.dumps(data, indent=2, ensure_ascii=True)
        except Exception:
            extra = ""

        return f"{notif.title}\n\n{notif.message}{extra}\n"

    @staticmethod
    def _send_email(msg: OutboxEmail) -> None:
        host = getattr(settings, "smtp_host", "")
        port = int(getattr(settings, "smtp_port", 587) or 587)
        user = getattr(settings, "smtp_user", "")
        password = getattr(settings, "smtp_password", "")
        from_addr = getattr(settings, "smtp_from", "") or user
        use_tls = bool(getattr(settings, "smtp_starttls", True))

        if not host or not from_addr:
            raise RuntimeError("SMTP not configured")

        email = EmailMessage()
        email["From"] = from_addr
        email["To"] = msg.to
        email["Subject"] = msg.subject
        email.set_content(msg.body)

        with smtplib.SMTP(host=host, port=port, timeout=10) as server:
            if use_tls:
                server.starttls()
            if user and password:
                server.login(user, password)
            server.send_message(email)
