-- ============================================
-- LaborGuard Initial Migration
-- Migration 001: Initial Schema
-- ============================================

-- This migration creates the initial database schema
-- Run against a fresh Supabase PostgreSQL instance

BEGIN;

-- Load the main schema
\i ../schema.sql

-- Load RLS policies
\i ../rls_policies.sql

-- ============================================
-- SEED: Default Zones for Chennai
-- ============================================
INSERT INTO zones (zone_code, city, area_name, sub_zone, latitude, longitude, radius_meters, flood_risk_score, heat_risk_score, aqi_risk_score, strike_frequency_yearly, overall_risk_level) VALUES
('CHN-VEL-4B', 'Chennai', 'Velachery', '4B', 12.9815, 80.2180, 500, 85.0, 45.0, 55.0, 1.5, 'HIGH'),
('CHN-VEL-4A', 'Chennai', 'Velachery', '4A', 12.9780, 80.2210, 500, 80.0, 44.0, 53.0, 1.5, 'HIGH'),
('CHN-ANN-2A', 'Chennai', 'Anna Nagar', '2A', 13.0850, 80.2101, 500, 35.0, 50.0, 60.0, 2.0, 'MEDIUM'),
('CHN-ANN-2B', 'Chennai', 'Anna Nagar', '2B', 13.0870, 80.2130, 500, 30.0, 48.0, 58.0, 2.0, 'MEDIUM'),
('CHN-TNR-1A', 'Chennai', 'T. Nagar', '1A', 13.0418, 80.2341, 500, 40.0, 52.0, 65.0, 1.0, 'MEDIUM'),
('CHN-ADY-3A', 'Chennai', 'Adyar', '3A', 13.0012, 80.2565, 500, 60.0, 42.0, 50.0, 0.5, 'MEDIUM'),
('CHN-MYL-5A', 'Chennai', 'Mylapore', '5A', 13.0368, 80.2676, 500, 45.0, 48.0, 55.0, 0.8, 'MEDIUM'),
('CHN-SHN-6A', 'Chennai', 'Sholinganallur', '6A', 12.9010, 80.2279, 500, 70.0, 46.0, 52.0, 0.3, 'HIGH'),
-- Bengaluru zones
('BLR-KOR-1A', 'Bengaluru', 'Koramangala', '1A', 12.9352, 77.6245, 500, 55.0, 35.0, 45.0, 1.0, 'MEDIUM'),
('BLR-IND-2A', 'Bengaluru', 'Indiranagar', '2A', 12.9784, 77.6408, 500, 40.0, 33.0, 48.0, 0.5, 'LOW'),
('BLR-WHT-3A', 'Bengaluru', 'Whitefield', '3A', 12.9698, 77.7500, 500, 50.0, 36.0, 55.0, 0.3, 'MEDIUM'),
('BLR-HSR-4A', 'Bengaluru', 'HSR Layout', '4A', 12.9116, 77.6389, 500, 60.0, 34.0, 50.0, 0.5, 'MEDIUM'),
-- Mumbai zones
('MUM-AND-1A', 'Mumbai', 'Andheri', '1A', 19.1136, 72.8697, 500, 75.0, 40.0, 70.0, 2.5, 'HIGH'),
('MUM-BAN-2A', 'Mumbai', 'Bandra', '2A', 19.0596, 72.8295, 500, 65.0, 38.0, 68.0, 2.0, 'HIGH'),
('MUM-DAD-3A', 'Mumbai', 'Dadar', '3A', 19.0176, 72.8562, 500, 70.0, 42.0, 72.0, 3.0, 'HIGH'),
-- Hyderabad zones
('HYD-HIB-1A', 'Hyderabad', 'HITEC City', '1A', 17.4435, 78.3772, 500, 30.0, 55.0, 50.0, 0.5, 'MEDIUM'),
('HYD-GAC-2A', 'Hyderabad', 'Gachibowli', '2A', 17.4401, 78.3489, 500, 35.0, 53.0, 48.0, 0.3, 'LOW'),
-- Delhi zones
('DEL-CON-1A', 'Delhi', 'Connaught Place', '1A', 28.6315, 77.2167, 500, 45.0, 60.0, 85.0, 3.0, 'HIGH'),
('DEL-SAK-2A', 'Delhi', 'Saket', '2A', 28.5244, 77.2066, 500, 40.0, 58.0, 80.0, 2.0, 'HIGH');

COMMIT;
