"""
LaborGuard JWT Authentication Middleware
OTP-based login, JWT tokens with 24-hour expiry, role-based access control
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from backend.config.settings import get_settings

security = HTTPBearer()
settings = get_settings()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=settings.jwt_expiry_hours))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Extract current user from JWT token."""
    payload = decode_token(credentials.credentials)
    worker_id = payload.get("sub")
    if worker_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return {
        "worker_id": worker_id,
        "role": payload.get("role", "WORKER"),
        "phone": payload.get("phone"),
        "name": payload.get("name"),
    }


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require ADMIN or SUPER_ADMIN role."""
    if current_user["role"] not in ("ADMIN", "SUPER_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def require_super_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require SUPER_ADMIN role."""
    if current_user["role"] != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )
    return current_user
