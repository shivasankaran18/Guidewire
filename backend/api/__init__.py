# backend/api/__init__.py
from .auth import router as auth_router
from .policies import router as policies_router
from .claims import router as claims_router
from .triggers import router as triggers_router
from .workers import router as workers_router
from .admin import router as admin_router
from .payouts import router as payouts_router

__all__ = [
    "auth_router",
    "policies_router",
    "claims_router",
    "triggers_router",
    "workers_router",
    "admin_router",
    "payouts_router",
]
