-- Migration 004: Add worker email + durable notifications

BEGIN;

-- 1) Worker email
ALTER TABLE workers
  ADD COLUMN IF NOT EXISTS email VARCHAR(320);

-- 2) Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    worker_id UUID NOT NULL REFERENCES workers(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    source_type VARCHAR(50),
    source_id VARCHAR(100),
    dedupe_key VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

-- Idempotency for notification creation
CREATE UNIQUE INDEX IF NOT EXISTS uq_worker_notification_dedupe
  ON notifications(worker_id, dedupe_key)
  WHERE dedupe_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_notifications_worker_created
  ON notifications(worker_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notifications_worker_unread
  ON notifications(worker_id)
  WHERE read_at IS NULL;

-- 3) Notification deliveries (channels)
CREATE TABLE IF NOT EXISTS notification_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_id UUID NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    next_attempt_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notification_deliveries_pending
  ON notification_deliveries(channel, status, next_attempt_at, created_at);

COMMIT;
