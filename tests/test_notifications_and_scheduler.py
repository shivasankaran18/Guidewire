import pytest

from sqlalchemy import select


@pytest.mark.asyncio
async def test_unread_count_and_mark_read(client, worker_headers):
    # Create a notification by exercising an existing workflow is hard in tests,
    # so we create one directly in the DB (same as real service behavior).
    from backend.models.database import async_session, Worker
    from backend.services.notification_service import NotificationService

    # Resolve current demo worker id
    prof = await client.get("/api/workers/profile", headers=worker_headers)
    assert prof.status_code == 200
    worker_id = prof.json()["id"]

    async with async_session() as db:
        w = (await db.execute(select(Worker).where(Worker.id == worker_id))).scalar_one()
        if not w.email:
            w.email = "ravi@example.com"
            await db.flush()

        await NotificationService.create_notification(
            db,
            worker_id,
            title="Test Inbox",
            message="This is a test",
            type="INFO",
            dedupe_key="test:inbox",
            send_email=False,
        )
        await db.commit()

    res = await client.get("/api/workers/notifications/unread-count", headers=worker_headers)
    assert res.status_code == 200
    assert res.json()["unread_count"] >= 1

    res_list = await client.get("/api/workers/notifications?limit=20", headers=worker_headers)
    assert res_list.status_code == 200
    items = res_list.json()["notifications"]
    nid = next(n["id"] for n in items if n["title"] == "Test Inbox")

    res_mark = await client.post(f"/api/workers/notifications/{nid}/read", headers=worker_headers)
    assert res_mark.status_code == 200

    res2 = await client.get("/api/workers/notifications/unread-count", headers=worker_headers)
    assert res2.status_code == 200
    assert res2.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_email_delivery_processor_marks_sent(monkeypatch, client, worker_headers):
    from backend.models.database import async_session, Worker, NotificationDelivery
    from backend.services.notification_service import NotificationService

    # Get worker id + ensure email exists
    prof = await client.get("/api/workers/profile", headers=worker_headers)
    worker_id = prof.json()["id"]

    sent_to = []

    def fake_send_email(msg):
        sent_to.append(msg.to)

    monkeypatch.setattr(NotificationService, "_send_email", staticmethod(fake_send_email))

    async with async_session() as db:
        w = (await db.execute(select(Worker).where(Worker.id == worker_id))).scalar_one()
        w.email = w.email or "ravi@example.com"
        await db.flush()

        notif = await NotificationService.create_notification(
            db,
            worker_id,
            title="Test Email",
            message="Email delivery should be SENT",
            type="ALERT",
            dedupe_key="test:email",
            send_email=True,
        )
        await db.commit()

        # Process pending deliveries
        async with async_session() as db2:
            res = await NotificationService.process_pending_email_deliveries(db2, limit=50)
            await db2.commit()
            assert res["sent"] >= 1

        # Verify delivery status
        async with async_session() as db3:
            q = select(NotificationDelivery).where(
                NotificationDelivery.notification_id == notif.id,
                NotificationDelivery.channel == "EMAIL",
            )
            d = (await db3.execute(q)).scalar_one()
            assert d.status == "SENT"

    assert sent_to and sent_to[0]


def test_scheduler_is_disabled_on_sqlite():
    # Scheduler uses Postgres advisory locks; on sqlite it should not start.
    from backend.services.scheduler import start_scheduler

    assert start_scheduler() is None
