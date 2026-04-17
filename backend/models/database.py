"""
LaborGuard Database Models & Connection
Async SQLAlchemy ORM with asyncpg for PostgreSQL
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    ForeignKey,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL", "")
# Strip any surrounding quotes
DATABASE_URL = DATABASE_URL.strip('"').strip("'")

# Convert postgres:// to postgresql+asyncpg://
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Remove params not supported by asyncpg
import re
# Remove channel_binding param
ASYNC_DATABASE_URL = re.sub(r'[&?]channel_binding=[^&]*', '', ASYNC_DATABASE_URL)
# Replace sslmode with ssl (asyncpg uses 'ssl' not 'sslmode')
ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace('sslmode=require', 'ssl=require')
# Fix possible broken query string (leading & without ?)
ASYNC_DATABASE_URL = re.sub(r'\?&', '?', ASYNC_DATABASE_URL)
# Remove trailing ? if no params left
if ASYNC_DATABASE_URL.endswith('?'):
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL[:-1]

engine = create_async_engine(ASYNC_DATABASE_URL, echo=False, pool_pre_ping=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


def generate_uuid():
    return str(uuid.uuid4())


# ─── Models ──────────────────────────────────────────────────────────────────

class Zone(Base):
    __tablename__ = "zones"

    id = Column(String, primary_key=True, default=generate_uuid)
    zone_code = Column(String, unique=True, nullable=False)
    city = Column(String, nullable=False)
    area_name = Column(String, nullable=False)
    sub_zone = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Integer, default=500)
    flood_risk_score = Column(Float, default=0)
    heat_risk_score = Column(Float, default=0)
    aqi_risk_score = Column(Float, default=0)
    strike_frequency_yearly = Column(Float, default=0)
    overall_risk_level = Column(String, default="LOW")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    workers = relationship("Worker", back_populates="zone")
    triggers = relationship("Trigger", back_populates="zone")


class Worker(Base):
    __tablename__ = "workers"

    id = Column(String, primary_key=True, default=generate_uuid)
    phone = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    platform = Column(String, nullable=True)
    platform_worker_id = Column(String, nullable=True)
    aadhaar_last4 = Column(String, nullable=True)
    aadhaar_hash = Column(String, nullable=True)
    upi_id_hash = Column(String, nullable=True)
    upi_id_masked = Column(String, nullable=True)
    email = Column(String, nullable=True)
    selfie_hash = Column(String, nullable=True)
    device_fingerprint = Column(String, nullable=True)
    device_model = Column(String, nullable=True)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=True)
    primary_zone_code = Column(String, nullable=True)
    avg_daily_earnings = Column(Float, default=0)
    avg_weekly_earnings = Column(Float, default=0)
    tenure_weeks = Column(Integer, default=0)
    trust_score = Column(Float, default=50.0)
    is_verified_partner = Column(Boolean, default=False)
    fraud_strikes = Column(Integer, default=0)
    account_status = Column(String, default="PROBATION")
    probation_end_date = Column(DateTime(timezone=True), nullable=True)
    role = Column(String, default="WORKER")
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    zone = relationship("Zone", back_populates="workers")
    policies = relationship("Policy", back_populates="worker")
    claims = relationship("Claim", back_populates="worker", foreign_keys="Claim.worker_id")
    reviewed_claims = relationship("Claim", back_populates="reviewer", foreign_keys="Claim.reviewed_by")
    resolved_fraud_rings = relationship("FraudRing", back_populates="resolver", foreign_keys="FraudRing.resolved_by")
    payouts = relationship("Payout", back_populates="worker")
    earnings_patterns = relationship("EarningsPattern", back_populates="worker")
    movement_signatures = relationship("MovementSignature", back_populates="worker")
    notifications = relationship("Notification", back_populates="worker")


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String, primary_key=True, default=generate_uuid)
    worker_id = Column(String, ForeignKey("workers.id"), nullable=False)
    plan_tier = Column(String, nullable=False)
    premium_amount = Column(Float, nullable=False)
    coverage_amount = Column(Float, nullable=False)
    coverage_multiplier = Column(Float, nullable=False)
    week_start = Column(String, nullable=False)
    week_end = Column(String, nullable=False)
    status = Column(String, default="ACTIVE")
    payment_reference = Column(String, nullable=True)
    payment_status = Column(String, default="PENDING")
    risk_factors = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    worker = relationship("Worker", back_populates="policies")
    claims = relationship("Claim", back_populates="policy")


class Trigger(Base):
    __tablename__ = "triggers"

    id = Column(String, primary_key=True, default=generate_uuid)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=False)
    zone_code = Column(String, nullable=False)
    trigger_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    threshold_value = Column(Float, nullable=True)
    threshold_limit = Column(Float, nullable=True)
    source_primary = Column(String, nullable=True)
    source_secondary = Column(String, nullable=True)
    source_tertiary = Column(String, nullable=True)
    sources_agreeing = Column(Integer, default=0)
    auto_approved = Column(Boolean, default=False)
    raw_data = Column(JSON, nullable=True)
    triggered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    zone = relationship("Zone", back_populates="triggers")
    claims = relationship("Claim", back_populates="trigger")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String, primary_key=True, default=generate_uuid)
    worker_id = Column(String, ForeignKey("workers.id"), nullable=False)
    policy_id = Column(String, ForeignKey("policies.id"), nullable=False)
    trigger_id = Column(String, ForeignKey("triggers.id"), nullable=False)
    zone_code = Column(String, nullable=False)
    claim_type = Column(String, nullable=False)
    disruption_hours = Column(Float, nullable=False)
    working_hours = Column(Float, default=10)
    earnings_for_slot = Column(Float, nullable=True)
    calculated_payout = Column(Float, nullable=False)
    actual_payout = Column(Float, nullable=True)
    payout_cap = Column(Float, nullable=True)
    fraud_score = Column(Float, default=0)
    fraud_tier = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    fraud_signals = Column(JSON, nullable=True)
    verification_method = Column(String, nullable=True)
    status = Column(String, default="PENDING")
    appeal_status = Column(String, nullable=True)
    appeal_reason = Column(String, nullable=True)
    reviewed_by = Column(String, ForeignKey("workers.id"), nullable=True)
    review_notes = Column(String, nullable=True)
    claimed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    worker = relationship("Worker", back_populates="claims", foreign_keys=[worker_id])
    reviewer = relationship("Worker", back_populates="reviewed_claims", foreign_keys=[reviewed_by])
    policy = relationship("Policy", back_populates="claims")
    trigger = relationship("Trigger", back_populates="claims")
    payout = relationship("Payout", back_populates="claim", uselist=False)


class Payout(Base):
    __tablename__ = "payouts"

    id = Column(String, primary_key=True, default=generate_uuid)
    claim_id = Column(String, ForeignKey("claims.id"), unique=True, nullable=False)
    worker_id = Column(String, ForeignKey("workers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    upi_reference = Column(String, nullable=True)
    payment_method = Column(String, default="UPI")
    payment_status = Column(String, default="PENDING")
    goodwill_credit = Column(Float, default=0)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    claim = relationship("Claim", back_populates="payout")
    worker = relationship("Worker", back_populates="payouts")


class EarningsPattern(Base):
    __tablename__ = "earnings_patterns"

    id = Column(String, primary_key=True, default=generate_uuid)
    worker_id = Column(String, ForeignKey("workers.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    hour_slot = Column(Integer, nullable=False)
    avg_earnings = Column(Float, default=0)
    order_count = Column(Integer, default=0)
    sample_weeks = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    worker = relationship("Worker", back_populates="earnings_patterns")

    __table_args__ = (
        UniqueConstraint("worker_id", "day_of_week", "hour_slot"),
    )


class FraudRing(Base):
    __tablename__ = "fraud_rings"

    id = Column(String, primary_key=True, default=generate_uuid)
    ring_id = Column(String, nullable=False)
    member_count = Column(Integer, nullable=False)
    detection_method = Column(String, nullable=True)
    center_latitude = Column(Float, nullable=True)
    center_longitude = Column(Float, nullable=True)
    radius_meters = Column(Integer, nullable=True)
    member_worker_ids = Column(JSON, nullable=False)
    shared_signals = Column(JSON, nullable=True)
    status = Column(String, default="DETECTED")
    frozen_amount = Column(Float, default=0)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(String, ForeignKey("workers.id"), nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    resolver = relationship("Worker", back_populates="resolved_fraud_rings", foreign_keys=[resolved_by])


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True, default=generate_uuid)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    actor_id = Column(String, nullable=True)
    actor_role = Column(String, nullable=True)
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    device_fingerprint = Column(String, nullable=True)
    entry_hash = Column(String, nullable=False)
    previous_hash = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    worker_id = Column(String, ForeignKey("workers.id"), nullable=False)
    type = Column(String, nullable=False)  # INFO, WARNING, ALERT, PAYOUT, COVERAGE
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    source_type = Column(String, nullable=True)
    source_id = Column(String, nullable=True)
    dedupe_key = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    read_at = Column(DateTime(timezone=True), nullable=True)

    worker = relationship("Worker", back_populates="notifications")
    deliveries = relationship("NotificationDelivery", back_populates="notification")

    __table_args__ = (
        UniqueConstraint("worker_id", "dedupe_key", name="uq_worker_notification_dedupe"),
    )


class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"

    id = Column(String, primary_key=True, default=generate_uuid)
    notification_id = Column(String, ForeignKey("notifications.id"), nullable=False)
    channel = Column(String, nullable=False)  # INBOX, EMAIL
    status = Column(String, default="PENDING", nullable=False)  # PENDING, SENT, FAILED, SKIPPED
    attempts = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    next_attempt_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    notification = relationship("Notification", back_populates="deliveries")


class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = Column(String, primary_key=True, default=generate_uuid)
    phone = Column(String, nullable=False)
    otp_hash = Column(String, nullable=False)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MovementSignature(Base):
    __tablename__ = "movement_signatures"

    id = Column(String, primary_key=True, default=generate_uuid)
    worker_id = Column(String, ForeignKey("workers.id"), nullable=False)
    signature_date = Column(String, nullable=False)
    avg_speed = Column(Float, nullable=True)
    stop_count = Column(Integer, nullable=True)
    route_complexity = Column(Float, nullable=True)
    active_hours = Column(Float, nullable=True)
    zones_visited = Column(JSON, nullable=True)
    gps_points_count = Column(Integer, nullable=True)
    altitude_variance = Column(Float, nullable=True)
    accelerometer_activity = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    worker = relationship("Worker", back_populates="movement_signatures")

    __table_args__ = (
        UniqueConstraint("worker_id", "signature_date"),
    )


# ─── DB Helpers ──────────────────────────────────────────────────────────────

async def init_db():
    """Create all tables.

    Note: This is safe for sqlite dev/test usage, but it is NOT a migration
    system for production Postgres. Prefer SQL migrations under `database/`.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Dispose the engine."""
    await engine.dispose()


async def get_db():
    """FastAPI dependency — yields an AsyncSession."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
