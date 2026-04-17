-- ============================================
-- GigPulse Sentinel Database Schema
-- Supabase PostgreSQL Compatible
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- ZONES TABLE
-- Geographic zone definitions with risk levels
-- ============================================
CREATE TABLE zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zone_code VARCHAR(20) UNIQUE NOT NULL,          -- e.g., "CHN-VEL-4B"
    city VARCHAR(100) NOT NULL,                      -- e.g., "Chennai"
    area_name VARCHAR(200) NOT NULL,                 -- e.g., "Velachery"
    sub_zone VARCHAR(10),                            -- e.g., "4B"
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    radius_meters INTEGER DEFAULT 500,               -- 500m polygon precision
    flood_risk_score DECIMAL(5, 2) DEFAULT 0,        -- 0-100
    heat_risk_score DECIMAL(5, 2) DEFAULT 0,         -- 0-100
    aqi_risk_score DECIMAL(5, 2) DEFAULT 0,          -- 0-100
    strike_frequency_yearly DECIMAL(5, 2) DEFAULT 0, -- avg strikes per year
    overall_risk_level VARCHAR(20) DEFAULT 'LOW',    -- LOW, MEDIUM, HIGH, CRITICAL
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- WORKERS TABLE
-- Worker profiles, device info, trust scores
-- ============================================
CREATE TABLE workers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(15) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    platform VARCHAR(50) NOT NULL,                   -- "zomato" or "swiggy"
    platform_worker_id VARCHAR(100) NOT NULL,        -- Zomato/Swiggy worker ID
    aadhaar_last4 VARCHAR(4),                        -- Masked Aadhaar (last 4 only)
    aadhaar_hash VARCHAR(256),                       -- SHA-256 hash of full Aadhaar
    upi_id_hash VARCHAR(256),                        -- Hashed UPI ID (never plaintext)
    upi_id_masked VARCHAR(50),                       -- e.g., "ravi****@upi"
    email VARCHAR(320),                              -- Optional email for notifications
    selfie_hash VARCHAR(256),                        -- Liveness check hash
    device_fingerprint VARCHAR(512),                 -- Unique device identifier
    device_model VARCHAR(200),
    zone_id UUID REFERENCES zones(id),
    primary_zone_code VARCHAR(20),
    avg_daily_earnings DECIMAL(10, 2) DEFAULT 0,
    avg_weekly_earnings DECIMAL(10, 2) DEFAULT 0,
    tenure_weeks INTEGER DEFAULT 0,
    trust_score DECIMAL(5, 2) DEFAULT 50.0,          -- 0-100
    is_verified_partner BOOLEAN DEFAULT false,       -- Trust > 80
    fraud_strikes INTEGER DEFAULT 0,                 -- 0-3 max
    account_status VARCHAR(20) DEFAULT 'PROBATION',  -- PROBATION, ACTIVE, SUSPENDED
    probation_end_date TIMESTAMP WITH TIME ZONE,
    role VARCHAR(20) DEFAULT 'WORKER',               -- WORKER, ADMIN, SUPER_ADMIN
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- NOTIFICATIONS TABLE
-- Durable inbox + delivery tracking
-- ============================================
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    worker_id UUID NOT NULL REFERENCES workers(id),
    type VARCHAR(50) NOT NULL,                       -- INFO, WARNING, ALERT, PAYOUT, COVERAGE
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    source_type VARCHAR(50),
    source_id VARCHAR(100),
    dedupe_key VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX uq_worker_notification_dedupe
  ON notifications(worker_id, dedupe_key)
  WHERE dedupe_key IS NOT NULL;

CREATE INDEX idx_notifications_worker_created
  ON notifications(worker_id, created_at DESC);

CREATE INDEX idx_notifications_worker_unread
  ON notifications(worker_id)
  WHERE read_at IS NULL;

CREATE TABLE notification_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_id UUID NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL,                    -- INBOX, EMAIL
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',   -- PENDING, SENT, FAILED, SKIPPED
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    next_attempt_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_notification_deliveries_pending
  ON notification_deliveries(channel, status, next_attempt_at, created_at);

-- ============================================
-- POLICIES TABLE
-- Weekly coverage policies
-- ============================================
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    worker_id UUID NOT NULL REFERENCES workers(id),
    plan_tier VARCHAR(20) NOT NULL,                  -- BASIC, STANDARD, PREMIUM
    premium_amount DECIMAL(10, 2) NOT NULL,          -- Weekly premium in INR
    coverage_amount DECIMAL(10, 2) NOT NULL,         -- Max payout for the week
    coverage_multiplier DECIMAL(3, 2) NOT NULL,      -- 1.0, 1.5, 2.0
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',             -- ACTIVE, EXPIRED, CANCELLED
    payment_reference VARCHAR(200),                  -- UPI transaction ref
    payment_status VARCHAR(20) DEFAULT 'PENDING',    -- PENDING, PAID, FAILED
    risk_factors JSONB,                              -- Breakdown of risk factors used
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- TRIGGERS TABLE
-- Parametric trigger events
-- ============================================
CREATE TABLE triggers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zone_id UUID NOT NULL REFERENCES zones(id),
    zone_code VARCHAR(20) NOT NULL,
    trigger_type VARCHAR(50) NOT NULL,               -- HEAVY_RAIN, FLOOD, HEAT, AQI, ORDER_SUSPENSION
    severity VARCHAR(20) NOT NULL,                   -- LOW, MODERATE, HIGH, CRITICAL
    threshold_value DECIMAL(10, 2),                  -- Actual measured value
    threshold_limit DECIMAL(10, 2),                  -- Configured threshold
    source_primary VARCHAR(100),                     -- Primary data source
    source_secondary VARCHAR(100),                   -- Secondary validation
    source_tertiary VARCHAR(100),                    -- Tertiary validation
    sources_agreeing INTEGER DEFAULT 0,              -- 1, 2, or 3
    auto_approved BOOLEAN DEFAULT false,
    raw_data JSONB,                                  -- Full API response data
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'ACTIVE',             -- ACTIVE, EXPIRED, CANCELLED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- CLAIMS TABLE
-- Claim records with fraud scores
-- ============================================
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    worker_id UUID NOT NULL REFERENCES workers(id),
    policy_id UUID NOT NULL REFERENCES policies(id),
    trigger_id UUID NOT NULL REFERENCES triggers(id),
    zone_code VARCHAR(20) NOT NULL,
    claim_type VARCHAR(50) NOT NULL,                 -- Maps to trigger_type
    disruption_hours DECIMAL(5, 2) NOT NULL,
    working_hours DECIMAL(5, 2) DEFAULT 10,
    earnings_for_slot DECIMAL(10, 2),                -- Earnings DNA value
    calculated_payout DECIMAL(10, 2) NOT NULL,
    actual_payout DECIMAL(10, 2),
    payout_cap DECIMAL(10, 2),                       -- 2x premium x multiplier
    fraud_score DECIMAL(5, 2) DEFAULT 0,             -- 0-100 (server-side only)
    fraud_tier VARCHAR(10),                          -- GREEN, AMBER, RED
    confidence_score DECIMAL(5, 2),                  -- Shown to worker (0-100)
    fraud_signals JSONB,                             -- Individual signal scores
    verification_method VARCHAR(50),                 -- AUTO, SOFT_VERIFY, MANUAL_REVIEW
    status VARCHAR(20) DEFAULT 'PENDING',            -- PENDING, APPROVED, REJECTED, APPEALED, PAID
    appeal_status VARCHAR(20),                       -- null, PENDING, APPROVED, REJECTED
    appeal_reason TEXT,
    reviewed_by UUID REFERENCES workers(id),         -- Admin who reviewed
    review_notes TEXT,
    claimed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- PAYOUTS TABLE
-- Payout records with UPI tracking
-- ============================================
CREATE TABLE payouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES claims(id),
    worker_id UUID NOT NULL REFERENCES workers(id),
    amount DECIMAL(10, 2) NOT NULL,
    upi_reference VARCHAR(200),
    payment_method VARCHAR(50) DEFAULT 'UPI',
    payment_status VARCHAR(20) DEFAULT 'PENDING',    -- PENDING, PROCESSING, COMPLETED, FAILED
    goodwill_credit DECIMAL(10, 2) DEFAULT 0,        -- ₹50 for false positive reversals
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- EARNINGS PATTERNS TABLE
-- Worker Earnings DNA data
-- ============================================
CREATE TABLE earnings_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    worker_id UUID NOT NULL REFERENCES workers(id),
    day_of_week INTEGER NOT NULL,                    -- 0=Monday, 6=Sunday
    hour_slot INTEGER NOT NULL,                      -- 0-23
    avg_earnings DECIMAL(10, 2) DEFAULT 0,
    order_count INTEGER DEFAULT 0,
    sample_weeks INTEGER DEFAULT 0,                  -- Number of weeks in average
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(worker_id, day_of_week, hour_slot)
);

-- ============================================
-- FRAUD RINGS TABLE
-- Detected fraud ring clusters
-- ============================================
CREATE TABLE fraud_rings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ring_id VARCHAR(100) NOT NULL,                   -- DBSCAN cluster ID
    member_count INTEGER NOT NULL,
    detection_method VARCHAR(50),                    -- SPATIAL_CLUSTER, IP_CORRELATION, TIMING_SYNC, etc.
    center_latitude DECIMAL(10, 7),
    center_longitude DECIMAL(10, 7),
    radius_meters INTEGER,
    member_worker_ids UUID[] NOT NULL,               -- Array of worker IDs
    shared_signals JSONB,                            -- Common fraud signals
    status VARCHAR(20) DEFAULT 'DETECTED',           -- DETECTED, INVESTIGATING, CONFIRMED, DISMISSED
    frozen_amount DECIMAL(12, 2) DEFAULT 0,          -- Total frozen payout amount
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES workers(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- AUDIT LOG TABLE
-- Immutable SHA-256 audit trail
-- ============================================
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,                -- CLAIM, PAYOUT, POLICY, WORKER, TRIGGER
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,                     -- CREATED, UPDATED, APPROVED, REJECTED, etc.
    actor_id UUID REFERENCES workers(id),
    actor_role VARCHAR(20),
    previous_state JSONB,
    new_state JSONB,
    ip_address VARCHAR(45),
    device_fingerprint VARCHAR(512),
    entry_hash VARCHAR(64) NOT NULL,                 -- SHA-256 hash
    previous_hash VARCHAR(64),                       -- Chain link to previous entry
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- OTP TABLE
-- Temporary OTP storage
-- ============================================
CREATE TABLE otp_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(15) NOT NULL,
    otp_hash VARCHAR(256) NOT NULL,                  -- Hashed OTP
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- MOVEMENT SIGNATURES TABLE
-- Worker movement baseline for fraud detection
-- ============================================
CREATE TABLE movement_signatures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    worker_id UUID NOT NULL REFERENCES workers(id),
    signature_date DATE NOT NULL,
    avg_speed DECIMAL(8, 2),                         -- km/h
    stop_count INTEGER,
    route_complexity DECIMAL(5, 2),                  -- 0-1 scale
    active_hours DECIMAL(4, 2),
    zones_visited VARCHAR(20)[],
    gps_points_count INTEGER,
    altitude_variance DECIMAL(8, 2),
    accelerometer_activity DECIMAL(5, 2),            -- 0-1 scale
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(worker_id, signature_date)
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_workers_phone ON workers(phone);
CREATE INDEX idx_workers_zone ON workers(zone_id);
CREATE INDEX idx_workers_status ON workers(account_status);
CREATE INDEX idx_policies_worker ON policies(worker_id);
CREATE INDEX idx_policies_week ON policies(week_start, week_end);
CREATE INDEX idx_policies_status ON policies(status);
CREATE INDEX idx_triggers_zone ON triggers(zone_id);
CREATE INDEX idx_triggers_type ON triggers(trigger_type);
CREATE INDEX idx_triggers_status ON triggers(status);
CREATE INDEX idx_claims_worker ON claims(worker_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_claims_fraud_tier ON claims(fraud_tier);
CREATE INDEX idx_payouts_worker ON payouts(worker_id);
CREATE INDEX idx_payouts_status ON payouts(payment_status);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_hash ON audit_log(entry_hash);
CREATE INDEX idx_otp_phone ON otp_codes(phone);
CREATE INDEX idx_earnings_worker ON earnings_patterns(worker_id);
CREATE INDEX idx_movement_worker ON movement_signatures(worker_id);
CREATE INDEX idx_notifications_worker ON notifications(worker_id);
