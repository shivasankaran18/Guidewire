"""
LaborGuard Database Models & Connection
SQLAlchemy ORM models matching the PostgreSQL schema
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey,
    create_engine, Index, UniqueConstraint
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from backend.config.settings import get_settings


class Base(DeclarativeBase):
    pass


# ============================================
# ZONES
# ============================================
class Zone(Base):
    __tablename__ = "zones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    zone_code = Column(String(20), unique=True, nullable=False)
    city = Column(String(100), nullable=False)
    area_name = Column(String(200), nullable=False)
    sub_zone = Column(String(10))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Integer, default=500)
    flood_risk_score = Column(Float, default=0)
    heat_risk_score = Column(Float, default=0)
    aqi_risk_score = Column(Float, default=0)
    strike_frequency_yearly = Column(Float, default=0)
    overall_risk_level = Column(String(20), default="LOW")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    workers = relationship("Worker", back_populates="zone")
    triggers = relationship("Trigger", back_populates="zone")


# ============================================
# WORKERS
# ============================================
class Worker(Base):
    __tablename__ = "workers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String(15), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    platform = Column(String(50), nullable=False)
    platform_worker_id = Column(String(100), nullable=False)
    aadhaar_last4 = Column(String(4))
    aadhaar_hash = Column(String(256))
    upi_id_hash = Column(String(256))
    upi_id_masked = Column(String(50))
    selfie_hash = Column(String(256))
    device_fingerprint = Column(String(512))
    device_model = Column(String(200))
    zone_id = Column(String(36), ForeignKey("zones.id"))
    primary_zone_code = Column(String(20))
    avg_daily_earnings = Column(Float, default=0)
    avg_weekly_earnings = Column(Float, default=0)
    tenure_weeks = Column(Integer, default=0)
    trust_score = Column(Float, default=50.0)
    is_verified_partner = Column(Boolean, default=False)
    fraud_strikes = Column(Integer, default=0)
    account_status = Column(String(20), default="PROBATION")
    probation_end_date = Column(DateTime)
    role = Column(String(20), default="WORKER")
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    zone = relationship("Zone", back_populates="workers")
    policies = relationship("Policy", back_populates="worker")
    claims = relationship("Claim", back_populates="worker", foreign_keys="Claim.worker_id")
    payouts = relationship("Payout", back_populates="worker")
    earnings_patterns = relationship("EarningsPattern", back_populates="worker")
    movement_signatures = relationship("MovementSignature", back_populates="worker")


# ============================================
# POLICIES
# ============================================
class Policy(Base):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(36), ForeignKey("workers.id"), nullable=False)
    plan_tier = Column(String(20), nullable=False)
    premium_amount = Column(Float, nullable=False)
    coverage_amount = Column(Float, nullable=False)
    coverage_multiplier = Column(Float, nullable=False)
    week_start = Column(String(10), nullable=False)
    week_end = Column(String(10), nullable=False)
    status = Column(String(20), default="ACTIVE")
    payment_reference = Column(String(200))
    payment_status = Column(String(20), default="PENDING")
    risk_factors = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    worker = relationship("Worker", back_populates="policies")
    claims = relationship("Claim", back_populates="policy")


# ============================================
# TRIGGERS
# ============================================
class Trigger(Base):
    __tablename__ = "triggers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    zone_id = Column(String(36), ForeignKey("zones.id"), nullable=False)
    zone_code = Column(String(20), nullable=False)
    trigger_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    threshold_value = Column(Float)
    threshold_limit = Column(Float)
    source_primary = Column(String(100))
    source_secondary = Column(String(100))
    source_tertiary = Column(String(100))
    sources_agreeing = Column(Integer, default=0)
    auto_approved = Column(Boolean, default=False)
    raw_data = Column(JSON)
    triggered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    zone = relationship("Zone", back_populates="triggers")
    claims = relationship("Claim", back_populates="trigger")


# ============================================
# CLAIMS
# ============================================
class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(36), ForeignKey("workers.id"), nullable=False)
    policy_id = Column(String(36), ForeignKey("policies.id"), nullable=False)
    trigger_id = Column(String(36), ForeignKey("triggers.id"), nullable=False)
    zone_code = Column(String(20), nullable=False)
    claim_type = Column(String(50), nullable=False)
    disruption_hours = Column(Float, nullable=False)
    working_hours = Column(Float, default=10)
    earnings_for_slot = Column(Float)
    calculated_payout = Column(Float, nullable=False)
    actual_payout = Column(Float)
    payout_cap = Column(Float)
    fraud_score = Column(Float, default=0)
    fraud_tier = Column(String(10))
    confidence_score = Column(Float)
    fraud_signals = Column(JSON)
    verification_method = Column(String(50))
    status = Column(String(20), default="PENDING")
    appeal_status = Column(String(20))
    appeal_reason = Column(Text)
    reviewed_by = Column(String(36), ForeignKey("workers.id"))
    review_notes = Column(Text)
    claimed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime)
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    worker = relationship("Worker", back_populates="claims", foreign_keys=[worker_id])
    policy = relationship("Policy", back_populates="claims")
    trigger = relationship("Trigger", back_populates="claims")
    payout = relationship("Payout", back_populates="claim", uselist=False)


# ============================================
# PAYOUTS
# ============================================
class Payout(Base):
    __tablename__ = "payouts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=False)
    worker_id = Column(String(36), ForeignKey("workers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    upi_reference = Column(String(200))
    payment_method = Column(String(50), default="UPI")
    payment_status = Column(String(20), default="PENDING")
    goodwill_credit = Column(Float, default=0)
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    claim = relationship("Claim", back_populates="payout")
    worker = relationship("Worker", back_populates="payouts")


# ============================================
# EARNINGS PATTERNS
# ============================================
class EarningsPattern(Base):
    __tablename__ = "earnings_patterns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(36), ForeignKey("workers.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    hour_slot = Column(Integer, nullable=False)
    avg_earnings = Column(Float, default=0)
    order_count = Column(Integer, default=0)
    sample_weeks = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("worker_id", "day_of_week", "hour_slot"),)

    worker = relationship("Worker", back_populates="earnings_patterns")


# ============================================
# FRAUD RINGS
# ============================================
class FraudRing(Base):
    __tablename__ = "fraud_rings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ring_id = Column(String(100), nullable=False)
    member_count = Column(Integer, nullable=False)
    detection_method = Column(String(50))
    center_latitude = Column(Float)
    center_longitude = Column(Float)
    radius_meters = Column(Integer)
    member_worker_ids = Column(JSON, nullable=False)
    shared_signals = Column(JSON)
    status = Column(String(20), default="DETECTED")
    frozen_amount = Column(Float, default=0)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime)
    resolved_by = Column(String(36), ForeignKey("workers.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ============================================
# AUDIT LOG
# ============================================
class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    action = Column(String(50), nullable=False)
    actor_id = Column(String(36))
    actor_role = Column(String(20))
    previous_state = Column(JSON)
    new_state = Column(JSON)
    ip_address = Column(String(45))
    device_fingerprint = Column(String(512))
    entry_hash = Column(String(64), nullable=False)
    previous_hash = Column(String(64))
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ============================================
# OTP CODES
# ============================================
class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String(15), nullable=False)
    otp_hash = Column(String(256), nullable=False)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ============================================
# MOVEMENT SIGNATURES
# ============================================
class MovementSignature(Base):
    __tablename__ = "movement_signatures"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(36), ForeignKey("workers.id"), nullable=False)
    signature_date = Column(String(10), nullable=False)
    avg_speed = Column(Float)
    stop_count = Column(Integer)
    route_complexity = Column(Float)
    active_hours = Column(Float)
    zones_visited = Column(JSON)
    gps_points_count = Column(Integer)
    altitude_variance = Column(Float)
    accelerometer_activity = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("worker_id", "signature_date"),)

    worker = relationship("Worker", back_populates="movement_signatures")


# ============================================
# DATABASE ENGINE & SESSION
# ============================================
settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
