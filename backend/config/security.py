"""
LaborGuard Config — Security
JWT + AES-256 encryption configuration
"""

import os
from datetime import timedelta

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
JWT_EXPIRY_DELTA = timedelta(hours=JWT_EXPIRY_HOURS)

# AES-256 Encryption for PII at rest
AES_ENCRYPTION_KEY = os.getenv("AES_ENCRYPTION_KEY", "dev-32-byte-aes-key-change-prod!")

# Secret key for general hashing
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# CORS origins
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

# Rate limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# OTP Configuration
OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_MAX_ATTEMPTS = 3

# TOTP for Admin 2FA
ADMIN_2FA_ENABLED = os.getenv("ADMIN_2FA_ENABLED", "false").lower() == "true"
