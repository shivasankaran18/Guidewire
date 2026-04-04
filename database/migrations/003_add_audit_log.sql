-- Migration 003: Add audit log table with SHA-256 hash chain
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    actor_id UUID REFERENCES workers(id),
    actor_role VARCHAR(20),
    previous_state JSONB,
    new_state JSONB,
    ip_address VARCHAR(45),
    device_fingerprint VARCHAR(512),
    entry_hash VARCHAR(64) NOT NULL,
    previous_hash VARCHAR(64),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_hash ON audit_log(entry_hash);
