"""Background scheduler for GigPulse Sentinel.

Runs periodic jobs (notifications delivery, nudges, etc.) in a multi-instance
safe manner by using Postgres advisory locks.

Important: we only start the scheduler if we can acquire a leader lock.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from sqlalchemy import text

from backend.models.database import async_session
from backend.services.notification_service import NotificationService
from backend.models.database import engine


LEADER_LOCK_KEY = 908_100_001
JOB_LOCK_EMAIL_DELIVERY = 908_100_002


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def _try_advisory_lock(db, key: int) -> bool:
    res = await db.execute(text("select pg_try_advisory_lock(:k)"), {"k": key})
    return bool(res.scalar())


async def _advisory_unlock(db, key: int) -> None:
    await db.execute(text("select pg_advisory_unlock(:k)"), {"k": key})


async def run_email_delivery_job() -> None:
    async with async_session() as session:
        # Take per-job lock to avoid duplicates during leader flaps.
        locked = await _try_advisory_lock(session, JOB_LOCK_EMAIL_DELIVERY)
        if not locked:
            return
        try:
            await NotificationService.process_pending_email_deliveries(session, limit=50)
        finally:
            await _advisory_unlock(session, JOB_LOCK_EMAIL_DELIVERY)


def start_scheduler() -> Optional[AsyncIOScheduler]:
    """Start APScheduler if leader lock acquired.

    Returns None when the DB is not Postgres (advisory locks unavailable).
    """

    # Advisory locks are Postgres-only. In dev/test we often run sqlite.
    if engine.url.get_backend_name() not in {"postgresql", "postgres"}:
        return None

    scheduler = AsyncIOScheduler(timezone="UTC")

    async def _maybe_start() -> None:
        # Advisory locks are connection-scoped; hold a dedicated connection.
        session = async_session()
        await session.__aenter__()
        locked = False
        try:
            locked = await _try_advisory_lock(session, LEADER_LOCK_KEY)
            if not locked:
                return

            scheduler.start()

            # Keep the connection alive for the lifetime of the app.
            while True:
                await asyncio.sleep(3600)
        finally:
            if locked:
                try:
                    await _advisory_unlock(session, LEADER_LOCK_KEY)
                except Exception:
                    pass
            await session.__aexit__(None, None, None)

    # Add jobs (scheduler.start happens only on leader)
    scheduler.add_job(
        run_email_delivery_job,
        trigger=IntervalTrigger(minutes=1),
        id="email_delivery",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )

    # In normal FastAPI runtime we have a running event loop.
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return None

    asyncio.create_task(_maybe_start())
    return scheduler
