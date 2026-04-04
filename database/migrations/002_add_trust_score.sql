-- Migration 002: Add trust score and enhanced worker fields
ALTER TABLE workers ADD COLUMN IF NOT EXISTS trust_score DECIMAL(5,2) DEFAULT 50.0;
ALTER TABLE workers ADD COLUMN IF NOT EXISTS is_verified_partner BOOLEAN DEFAULT false;
ALTER TABLE workers ADD COLUMN IF NOT EXISTS fraud_strikes INTEGER DEFAULT 0;
ALTER TABLE workers ADD COLUMN IF NOT EXISTS probation_end_date TIMESTAMP WITH TIME ZONE;
