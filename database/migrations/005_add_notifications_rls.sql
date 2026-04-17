-- Migration 005: RLS for notifications tables
-- Supabase/Postgres: enable RLS + add policies (idempotent)

BEGIN;

-- Enable RLS (safe to re-run)
ALTER TABLE IF EXISTS notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS notification_deliveries ENABLE ROW LEVEL SECURITY;

-- notifications_select_own
DO $$
BEGIN
  IF to_regclass('public.notifications') IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'notifications' AND policyname = 'notifications_select_own'
  ) THEN
    CREATE POLICY notifications_select_own ON notifications
      FOR SELECT USING (worker_id = auth.uid());
  END IF;
END
$$;

-- notifications_update_own (mark read)
DO $$
BEGIN
  IF to_regclass('public.notifications') IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'notifications' AND policyname = 'notifications_update_own'
  ) THEN
    CREATE POLICY notifications_update_own ON notifications
      FOR UPDATE USING (worker_id = auth.uid())
      WITH CHECK (worker_id = auth.uid());
  END IF;
END
$$;

-- notifications_admin_select
DO $$
BEGIN
  IF to_regclass('public.notifications') IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'notifications' AND policyname = 'notifications_admin_select'
  ) THEN
    CREATE POLICY notifications_admin_select ON notifications
      FOR SELECT USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
      );
  END IF;
END
$$;

-- notification_deliveries_admin_only
DO $$
BEGIN
  IF to_regclass('public.notification_deliveries') IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'notification_deliveries' AND policyname = 'notification_deliveries_admin_only'
  ) THEN
    CREATE POLICY notification_deliveries_admin_only ON notification_deliveries
      FOR ALL USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
      );
  END IF;
END
$$;

COMMIT;
