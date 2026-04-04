-- ============================================
-- LaborGuard Seed Data
-- Demo workers + zones for presentation
-- ============================================

-- Demo Worker: Ravi Kumar (our persona)
INSERT INTO workers (id, phone, name, platform, platform_worker_id, aadhaar_last4, upi_id_masked, primary_zone_code, avg_daily_earnings, avg_weekly_earnings, tenure_weeks, trust_score, is_verified_partner, account_status, role)
VALUES
('demo-ravi-001', '+919876543210', 'Ravi Kumar', 'zomato', 'ZW123456', '4321', 'ravi****@upi', 'CHN-VEL-4B', 700, 4200, 24, 78.5, false, 'ACTIVE', 'WORKER'),
('demo-priya-002', '+919876543211', 'Priya Sharma', 'swiggy', 'SW234567', '5678', 'priya****@upi', 'CHN-ANN-2A', 650, 3900, 36, 85.0, true, 'ACTIVE', 'WORKER'),
('demo-arjun-003', '+919876543212', 'Arjun Reddy', 'zomato', 'ZW345678', '9012', 'arjun****@upi', 'BLR-KOR-1A', 800, 4800, 52, 92.0, true, 'ACTIVE', 'WORKER'),
('demo-karthik-004', '+919876543213', 'Karthik Nair', 'swiggy', 'SW456789', '3456', 'karthi****@upi', 'MUM-AND-1A', 750, 4500, 8, 55.0, false, 'ACTIVE', 'WORKER'),
('demo-suresh-005', '+919876543214', 'Suresh Yadav', 'zomato', 'ZW567890', '7890', 'suresh****@upi', 'DEL-CON-1A', 680, 4080, 16, 42.0, false, 'ACTIVE', 'WORKER');

-- Demo Admin
INSERT INTO workers (id, phone, name, platform, platform_worker_id, primary_zone_code, trust_score, account_status, role)
VALUES
('demo-admin-001', '+919999900001', 'Admin Priya', 'zomato', 'ADMIN001', 'CHN-ANN-2A', 100, 'ACTIVE', 'ADMIN'),
('demo-sadmin-001', '+919999900000', 'Super Admin', 'zomato', 'SADMIN001', 'CHN-ANN-2A', 100, 'ACTIVE', 'SUPER_ADMIN');

-- Demo Policies
INSERT INTO policies (id, worker_id, plan_tier, premium_amount, coverage_amount, coverage_multiplier, week_start, week_end, status, payment_status, payment_reference)
VALUES
('demo-pol-001', 'demo-ravi-001', 'STANDARD', 59, 6300, 1.5, '2026-03-30', '2026-04-05', 'ACTIVE', 'PAID', 'UPI_DEMO001'),
('demo-pol-002', 'demo-priya-002', 'PREMIUM', 72, 7800, 2.0, '2026-03-30', '2026-04-05', 'ACTIVE', 'PAID', 'UPI_DEMO002'),
('demo-pol-003', 'demo-arjun-003', 'BASIC', 35, 4800, 1.0, '2026-03-30', '2026-04-05', 'ACTIVE', 'PAID', 'UPI_DEMO003');

-- Demo Triggers
INSERT INTO triggers (id, zone_id, zone_code, trigger_type, severity, threshold_value, threshold_limit, sources_agreeing, auto_approved, status)
VALUES
('demo-trig-001', (SELECT id FROM zones WHERE zone_code='CHN-VEL-4B'), 'CHN-VEL-4B', 'HEAVY_RAIN', 'HIGH', 95.5, 80, 3, true, 'ACTIVE'),
('demo-trig-002', (SELECT id FROM zones WHERE zone_code='DEL-CON-1A'), 'DEL-CON-1A', 'AQI', 'CRITICAL', 435, 400, 3, true, 'ACTIVE');
