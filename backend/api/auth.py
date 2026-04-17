"""
GigPulse Sentinel Auth API
OTP-based login, registration, JWT token management
"""

import uuid
import hashlib
import random
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Worker, OTPCode, get_db
from backend.models.schemas import (
    SendOTPRequest, VerifyOTPRequest, RegisterRequest,
    AuthResponse, OTPResponse, MessageResponse,
)
from backend.middleware.auth_middleware import create_access_token
from backend.services.audit_logger import AuditLogger

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory OTP store for demo
_demo_otps: dict[str, str] = {}


@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(request: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    """Send OTP to phone number for login/registration."""
    phone = request.phone.strip()
    if not phone.startswith('+91'):
        phone = f'+91{phone.lstrip("91")}'

    otp = str(random.randint(100000, 999999))
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()

    _demo_otps[phone] = otp

    otp_record = OTPCode(
        id=str(uuid.uuid4()),
        phone=phone,
        otp_hash=otp_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    db.add(otp_record)
    await db.flush()

    return OTPResponse(
        message=f"OTP sent to {phone}. Demo OTP: {otp}",
        expires_in_seconds=300,
    )


@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    """Verify OTP and return JWT token."""
    phone = request.phone.strip()
    if not phone.startswith('+91'):
        phone = f'+91{phone.lstrip("91")}'

    stored_otp = _demo_otps.get(phone)
    if not stored_otp or stored_otp != request.otp:
        otp_hash = hashlib.sha256(request.otp.encode()).hexdigest()
        result = await db.execute(
            select(OTPCode).where(
                OTPCode.phone == phone,
                OTPCode.otp_hash == otp_hash,
                OTPCode.used == False,
                OTPCode.expires_at > datetime.now(timezone.utc),
            )
        )
        otp_record = result.scalar_one_or_none()
        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired OTP",
            )
        otp_record.used = True
        await db.flush()
    else:
        del _demo_otps[phone]

    result = await db.execute(select(Worker).where(Worker.phone == phone))
    worker = result.scalar_one_or_none()

    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not registered. Please register first.",
        )

    worker.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    token = create_access_token({
        "sub": worker.id, "phone": worker.phone,
        "name": worker.name, "role": worker.role,
    })

    await AuditLogger.log(
        db, "WORKER", worker.id, "LOGIN",
        actor_id=worker.id, actor_role=worker.role,
    )

    return AuthResponse(
        access_token=token, worker_id=worker.id,
        role=worker.role, name=worker.name,
    )


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new worker."""
    phone = request.phone.strip()
    if not phone.startswith('+91'):
        phone = f'+91{phone.lstrip("91")}'

    result = await db.execute(select(Worker).where(Worker.phone == phone))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered",
        )

    worker_id = str(uuid.uuid4())
    worker = Worker(
        id=worker_id, phone=phone, name=request.name,
        platform=request.platform,
        platform_worker_id=request.platform_worker_id,
        aadhaar_last4=request.aadhaar_last4,
        aadhaar_hash=hashlib.sha256((request.aadhaar_last4 or "").encode()).hexdigest() if request.aadhaar_last4 else None,
        upi_id_hash=hashlib.sha256((request.upi_id or "").encode()).hexdigest() if request.upi_id else None,
        upi_id_masked=f"{request.name[:4].lower()}****@upi" if request.upi_id else None,
        device_fingerprint=request.device_fingerprint,
        device_model=request.device_model,
        primary_zone_code=request.zone_code or "CHN-VEL-4B",
        avg_daily_earnings=700, avg_weekly_earnings=4200,
        trust_score=50.0, account_status="PROBATION",
        probation_end_date=datetime.now(timezone.utc) + timedelta(weeks=2),
        role="WORKER",
    )
    db.add(worker)
    await db.flush()

    await AuditLogger.log(
        db, "WORKER", worker_id, "REGISTERED",
        actor_id=worker_id,
        new_state={"phone": phone, "name": request.name, "platform": request.platform},
    )

    token = create_access_token({
        "sub": worker_id, "phone": phone,
        "name": request.name, "role": "WORKER",
    })

    return AuthResponse(
        access_token=token, worker_id=worker_id,
        role="WORKER", name=request.name,
    )


@router.post("/demo-login", response_model=AuthResponse)
async def demo_login(db: AsyncSession = Depends(get_db)):
    """Quick demo login — creates or logs into demo worker account."""
    demo_phone = "+919876543210"
    result = await db.execute(select(Worker).where(Worker.phone == demo_phone))
    worker = result.scalar_one_or_none()

    if not worker:
        worker = Worker(
            id=str(uuid.uuid4()), phone=demo_phone, name="Ravi Kumar",
            platform="zomato", platform_worker_id="ZW123456",
            aadhaar_last4="4321", upi_id_masked="ravi****@upi",
            email="ravi@example.com",
            primary_zone_code="CHN-VEL-4B",
            avg_daily_earnings=700, avg_weekly_earnings=4200,
            tenure_weeks=24, trust_score=78.5,
            account_status="ACTIVE", role="WORKER",
        )
        db.add(worker)
        await db.flush()

    token = create_access_token({
        "sub": worker.id, "phone": worker.phone,
        "name": worker.name, "role": worker.role,
    })
    return AuthResponse(
        access_token=token, worker_id=worker.id,
        role=worker.role, name=worker.name,
    )


@router.post("/demo-admin-login", response_model=AuthResponse)
async def demo_admin_login(db: AsyncSession = Depends(get_db)):
    """Quick demo admin login."""
    admin_phone = "+919999900001"
    result = await db.execute(select(Worker).where(Worker.phone == admin_phone))
    worker = result.scalar_one_or_none()

    if not worker:
        worker = Worker(
            id=str(uuid.uuid4()), phone=admin_phone, name="Admin Priya",
            platform="zomato", platform_worker_id="ADMIN001",
            email="admin@example.com",
            primary_zone_code="CHN-ANN-2A",
            trust_score=100, account_status="ACTIVE", role="ADMIN",
        )
        db.add(worker)
        await db.flush()

    token = create_access_token({
        "sub": worker.id, "phone": worker.phone,
        "name": worker.name, "role": worker.role,
    })
    return AuthResponse(
        access_token=token, worker_id=worker.id,
        role=worker.role, name=worker.name,
    )
