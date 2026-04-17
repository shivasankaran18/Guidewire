"""
GigPulse Sentinel Backend Configuration
Environment-based settings management
"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "GigPulse Sentinel"
    app_version: str = "1.0.0"
    debug: bool = True
    backend_port: int = 8000

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_secret: str = "dev-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    aes_encryption_key: str = "dev-32-byte-aes-key-change-prod!"

    # Database
    database_url: str = os.getenv("DATABASE_URL", "")

    # Supabase (optional, for production)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    # External APIs - set to real key for live weather data, or "mock" for mock mode
    openweathermap_api_key: str = "mock"
    aqicn_api_key: str = "mock"
    imd_api_base_url: str = "http://localhost:8000/mock/imd"
    zomato_api_base_url: str = "http://localhost:8000/mock/zomato"

    # Payment
    razorpay_key_id: str = "rzp_test_mock"
    razorpay_key_secret: str = "mock_secret"

    # AI Agents (Cerebras)
    cerebras_api_key: str = ""

    # Mock mode
    use_mock_apis: bool = True

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Rate limiting
    rate_limit_per_minute: int = 60

    # Email (SMTP)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_starttls: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
