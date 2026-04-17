-- ============================================
-- GigPulse Sentinel Row Level Security Policies
-- Supabase RLS Configuration
-- ============================================

-- Enable RLS on all tables
ALTER TABLE workers ENABLE ROW LEVEL SECURITY;
ALTER TABLE policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE triggers ENABLE ROW LEVEL SECURITY;
ALTER TABLE payouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE earnings_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE fraud_rings ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE movement_signatures ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_deliveries ENABLE ROW LEVEL SECURITY;

-- ============================================
-- WORKERS RLS
-- ============================================
-- Workers can read their own profile
CREATE POLICY workers_select_own ON workers
    FOR SELECT USING (id = auth.uid());

-- Workers can update their own profile (limited fields)
CREATE POLICY workers_update_own ON workers
    FOR UPDATE USING (id = auth.uid())
    WITH CHECK (id = auth.uid());

-- Admins can read all workers
CREATE POLICY workers_admin_select ON workers
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- Admins can update workers
CREATE POLICY workers_admin_update ON workers
    FOR UPDATE USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- ============================================
-- POLICIES RLS
-- ============================================
-- Workers can read their own policies
CREATE POLICY policies_select_own ON policies
    FOR SELECT USING (worker_id = auth.uid());

-- Workers can create policies for themselves
CREATE POLICY policies_insert_own ON policies
    FOR INSERT WITH CHECK (worker_id = auth.uid());

-- Admins can read all policies
CREATE POLICY policies_admin_select ON policies
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- ============================================
-- CLAIMS RLS
-- ============================================
-- Workers can read their own claims
CREATE POLICY claims_select_own ON claims
    FOR SELECT USING (worker_id = auth.uid());

-- Workers can create claims for themselves
CREATE POLICY claims_insert_own ON claims
    FOR INSERT WITH CHECK (worker_id = auth.uid());

-- Workers can update their own claims (for appeals)
CREATE POLICY claims_update_own ON claims
    FOR UPDATE USING (worker_id = auth.uid())
    WITH CHECK (worker_id = auth.uid());

-- Admins can read all claims
CREATE POLICY claims_admin_select ON claims
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- Admins can update claims (resolve/review)
CREATE POLICY claims_admin_update ON claims
    FOR UPDATE USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- ============================================
-- TRIGGERS RLS
-- ============================================
-- All authenticated users can read triggers (public data)
CREATE POLICY triggers_select_all ON triggers
    FOR SELECT USING (true);

-- Only system/admin can insert triggers
CREATE POLICY triggers_admin_insert ON triggers
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- ============================================
-- PAYOUTS RLS
-- ============================================
-- Workers can read their own payouts
CREATE POLICY payouts_select_own ON payouts
    FOR SELECT USING (worker_id = auth.uid());

-- Admins can read all payouts
CREATE POLICY payouts_admin_select ON payouts
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- ============================================
-- EARNINGS PATTERNS RLS
-- ============================================
-- Workers can read their own earnings patterns
CREATE POLICY earnings_select_own ON earnings_patterns
    FOR SELECT USING (worker_id = auth.uid());

-- Admins can read all patterns
CREATE POLICY earnings_admin_select ON earnings_patterns
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- ============================================
-- FRAUD RINGS RLS
-- ============================================
-- Only admins can access fraud ring data
CREATE POLICY fraud_rings_admin_only ON fraud_rings
    FOR ALL USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- ============================================
-- AUDIT LOG RLS
-- ============================================
-- Audit logs are INSERT-ONLY (immutable)
-- Only system can insert
CREATE POLICY audit_insert_only ON audit_log
    FOR INSERT WITH CHECK (true);

-- Admins can read audit logs
CREATE POLICY audit_admin_select ON audit_log
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- No updates or deletes allowed on audit_log
-- (Immutable by design - no UPDATE or DELETE policies)

-- ============================================
-- MOVEMENT SIGNATURES RLS
-- ============================================
-- Workers can read their own movement data
CREATE POLICY movement_select_own ON movement_signatures
    FOR SELECT USING (worker_id = auth.uid());

-- Admins can read all movement data
CREATE POLICY movement_admin_select ON movement_signatures
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- ============================================
-- NOTIFICATIONS RLS
-- ============================================
-- Workers can read their own notifications
CREATE POLICY notifications_select_own ON notifications
    FOR SELECT USING (worker_id = auth.uid());

-- Workers can update their own notifications (mark read)
CREATE POLICY notifications_update_own ON notifications
    FOR UPDATE USING (worker_id = auth.uid())
    WITH CHECK (worker_id = auth.uid());

-- Admins can read all notifications
CREATE POLICY notifications_admin_select ON notifications
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );

-- Notification deliveries: admins only (system job)
CREATE POLICY notification_deliveries_admin_only ON notification_deliveries
    FOR ALL USING (
        EXISTS (SELECT 1 FROM workers WHERE id = auth.uid() AND role IN ('ADMIN', 'SUPER_ADMIN'))
    );
