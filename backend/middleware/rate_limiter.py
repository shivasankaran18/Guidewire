"""
LaborGuard Rate Limiter Middleware
Simple in-memory rate limiting per IP/user
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from backend.config.settings import get_settings

settings = get_settings()


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limit API requests per IP address."""

    def __init__(self, app, requests_per_minute: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.rate_limit_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Clean old entries
        now = time.time()
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if now - t < 60
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )

        # Record request
        self.requests[client_ip].append(now)

        # Process request
        response = await call_next(request)
        return response
