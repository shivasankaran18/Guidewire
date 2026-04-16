"""
GigPulse Sentinel Device Fingerprint Middleware
One Device = One Account enforcement
"""

import hashlib
from fastapi import Request, HTTPException, status
from sqlalchemy import select
from backend.models.database import Worker, async_session


def generate_device_fingerprint(
    user_agent: str = "", screen_resolution: str = "",
    platform: str = "", hardware_concurrency: str = "",
    device_model: str = "",
) -> str:
    """Generate a device fingerprint hash from device attributes."""
    raw = f"{user_agent}|{screen_resolution}|{platform}|{hardware_concurrency}|{device_model}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def validate_device_fingerprint(worker_id: str, device_fingerprint: str) -> dict:
    """Validate that the device fingerprint matches the registered device."""
    async with async_session() as session:
        result = await session.execute(select(Worker).where(Worker.id == worker_id))
        worker = result.scalar_one_or_none()

        if not worker:
            return {"valid": False, "reason": "Worker not found"}

        if not worker.device_fingerprint:
            worker.device_fingerprint = device_fingerprint
            await session.commit()
            return {"valid": True, "reason": "Device registered"}

        if worker.device_fingerprint == device_fingerprint:
            return {"valid": True, "reason": "Device matched"}

        return {
            "valid": False,
            "reason": "Device mismatch — One Device = One Account policy",
            "registered_device": worker.device_fingerprint[:8] + "...",
            "current_device": device_fingerprint[:8] + "...",
        }


def detect_mock_gps(device_info: dict) -> dict:
    """Check for signs of GPS spoofing or rooted device."""
    suspicious_signals = []
    risk_score = 0

    if device_info.get("is_rooted", False):
        suspicious_signals.append("Device appears to be rooted")
        risk_score += 40

    mock_apps = device_info.get("installed_apps", [])
    known_spoof_apps = ["fake gps", "mock locations", "gps joystick", "fly gps", "location changer", "fake location"]
    for app in mock_apps:
        if any(spoof in app.lower() for spoof in known_spoof_apps):
            suspicious_signals.append(f"Spoofing app detected: {app}")
            risk_score += 30

    if device_info.get("mock_location_enabled", False):
        suspicious_signals.append("Mock location setting is enabled")
        risk_score += 25

    if device_info.get("is_emulator", False):
        suspicious_signals.append("Running on emulator")
        risk_score += 35

    return {"is_suspicious": risk_score > 20, "risk_score": min(risk_score, 100), "signals": suspicious_signals}
