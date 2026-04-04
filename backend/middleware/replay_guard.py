"""
LaborGuard Replay Guard Middleware
Nonce + timestamp deduplication — replay attacks rejected silently
"""

import time
import hashlib
from collections import OrderedDict
from fastapi import Request, HTTPException, status


class ReplayGuard:
    """
    Prevents replay attacks using nonce + timestamp deduplication.
    Each API request must include a unique nonce and a recent timestamp.
    """

    def __init__(self, max_age_seconds: int = 300, max_nonces: int = 10000):
        self.max_age = max_age_seconds
        self.max_nonces = max_nonces
        self._seen_nonces: OrderedDict[str, float] = OrderedDict()

    def validate_request(
        self,
        nonce: str,
        timestamp: float,
        worker_id: str = "",
        device_fingerprint: str = "",
    ) -> dict:
        """
        Validate a request against replay attacks.
        Returns validation result.
        """
        now = time.time()

        # Check timestamp freshness
        if abs(now - timestamp) > self.max_age:
            return {
                "valid": False,
                "reason": f"Request timestamp too old (>{self.max_age}s)",
                "age_seconds": round(abs(now - timestamp), 1),
            }

        # Build composite nonce key
        nonce_key = hashlib.sha256(
            f"{nonce}:{worker_id}:{device_fingerprint}:{timestamp}".encode()
        ).hexdigest()

        # Check for replay
        if nonce_key in self._seen_nonces:
            return {
                "valid": False,
                "reason": "Duplicate nonce — replay attack detected",
                "nonce": nonce_key[:16] + "...",
            }

        # Store nonce
        self._seen_nonces[nonce_key] = now

        # Cleanup old nonces
        self._cleanup()

        return {"valid": True, "nonce": nonce_key[:16] + "..."}

    def _cleanup(self):
        """Remove expired nonces to prevent memory growth."""
        now = time.time()
        while self._seen_nonces:
            oldest_key, oldest_time = next(iter(self._seen_nonces.items()))
            if now - oldest_time > self.max_age:
                self._seen_nonces.pop(oldest_key)
            else:
                break

        # Hard cap on size
        while len(self._seen_nonces) > self.max_nonces:
            self._seen_nonces.popitem(last=False)


# Global guard instance
replay_guard = ReplayGuard()
