"""
Gigpulse Sentinel Backend - Main FastAPI Application
AI-Powered Parametric Income Protection for Gig Delivery Workers
"""

from contextlib import asynccontextmanager
import sys
import uuid
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import get_settings
from backend.models.database import init_db, close_db, async_session, Zone
from backend.middleware.rate_limiter import RateLimiterMiddleware
from backend.services.scheduler import start_scheduler
from backend.api import (
    auth_router, policies_router, claims_router,
    triggers_router, workers_router, admin_router,
    payouts_router, agents_router,
)
from sqlalchemy import select

settings = get_settings()


def _database_label(database_url: str) -> str:
    url = (database_url or "").lower()
    if url.startswith("sqlite"):
        return "SQLite"
    if "postgres" in url:
        return "PostgreSQL"
    return "Unknown"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle - initialize DB on startup."""
    await init_db()
    print("🛡️ GigPulse Sentinel Backend Started")
    print(f"📊 Database: {_database_label(settings.database_url)}")
    print(f"🔧 Mock APIs: {'Enabled' if settings.use_mock_apis else 'Disabled'}")

    # Seed zones on startup
    async with async_session() as session:
        result = await session.execute(select(Zone).limit(1))
        if not result.scalar_one_or_none():
            await _seed_zones(session)
            await session.commit()
            print("🌍 Seeded default zones")

    # Start background scheduler (leader-only in multi-instance)
    scheduler = start_scheduler()

    yield

    try:
        if scheduler and scheduler.running:
            scheduler.shutdown(wait=False)
    except Exception:
        pass
    await close_db()
    print("🛡️ GigPulse Sentinel Backend Shutting Down")


app = FastAPI(
    title="GigPulse Sentinel API",
    description="AI-Powered Parametric Income Protection for Gig Delivery Workers",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter
app.add_middleware(RateLimiterMiddleware)

# API Routes
app.include_router(auth_router, prefix="/api")
app.include_router(policies_router, prefix="/api")
app.include_router(claims_router, prefix="/api")
app.include_router(triggers_router, prefix="/api")
app.include_router(workers_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(payouts_router, prefix="/api")

# Mock APIs (if enabled)
if settings.use_mock_apis:
    mock_apis_dir = Path(__file__).resolve().parent.parent / "mock-apis"
    if mock_apis_dir.exists() and str(mock_apis_dir) not in sys.path:
        sys.path.append(str(mock_apis_dir))

    from weather_api import router as weather_mock
    from imd_api import router as imd_mock
    from aqicn_api import router as aqicn_mock
    from zomato_api import router as zomato_mock
    from razorpay_api import router as razorpay_mock
    app.include_router(weather_mock)
    app.include_router(imd_mock)
    app.include_router(aqicn_mock)
    app.include_router(zomato_mock)
    app.include_router(razorpay_mock)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "app": "GigPulse Sentinel",
        "version": "1.0.0",
        "status": "running",
        "description": "AI-Powered Parametric Income Protection for Gig Delivery Workers",
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


async def _seed_zones(session):
    """Seed default zones."""
    zones_data = [
        ("CHN-VEL-4B", "Chennai", "Velachery", "4B", 12.9815, 80.2180, 85, 45, 55, 1.5, "HIGH"),
        ("CHN-VEL-4A", "Chennai", "Velachery", "4A", 12.9780, 80.2210, 80, 44, 53, 1.5, "HIGH"),
        ("CHN-ANN-2A", "Chennai", "Anna Nagar", "2A", 13.0850, 80.2101, 35, 50, 60, 2.0, "MEDIUM"),
        ("CHN-ANN-2B", "Chennai", "Anna Nagar", "2B", 13.0870, 80.2130, 30, 48, 58, 2.0, "MEDIUM"),
        ("CHN-TNR-1A", "Chennai", "T. Nagar", "1A", 13.0418, 80.2341, 40, 52, 65, 1.0, "MEDIUM"),
        ("CHN-ADY-3A", "Chennai", "Adyar", "3A", 13.0012, 80.2565, 60, 42, 50, 0.5, "MEDIUM"),
        ("CHN-MYL-5A", "Chennai", "Mylapore", "5A", 13.0368, 80.2676, 45, 48, 55, 0.8, "MEDIUM"),
        ("CHN-SHN-6A", "Chennai", "Sholinganallur", "6A", 12.9010, 80.2279, 70, 46, 52, 0.3, "HIGH"),
        ("BLR-KOR-1A", "Bengaluru", "Koramangala", "1A", 12.9352, 77.6245, 55, 35, 45, 1.0, "MEDIUM"),
        ("BLR-IND-2A", "Bengaluru", "Indiranagar", "2A", 12.9784, 77.6408, 40, 33, 48, 0.5, "LOW"),
        ("BLR-WHT-3A", "Bengaluru", "Whitefield", "3A", 12.9698, 77.7500, 50, 36, 55, 0.3, "MEDIUM"),
        ("BLR-HSR-4A", "Bengaluru", "HSR Layout", "4A", 12.9116, 77.6389, 60, 34, 50, 0.5, "MEDIUM"),
        ("MUM-AND-1A", "Mumbai", "Andheri", "1A", 19.1136, 72.8697, 75, 40, 70, 2.5, "HIGH"),
        ("MUM-BAN-2A", "Mumbai", "Bandra", "2A", 19.0596, 72.8295, 65, 38, 68, 2.0, "HIGH"),
        ("MUM-DAD-3A", "Mumbai", "Dadar", "3A", 19.0176, 72.8562, 70, 42, 72, 3.0, "HIGH"),
        ("HYD-HIB-1A", "Hyderabad", "HITEC City", "1A", 17.4435, 78.3772, 30, 55, 50, 0.5, "MEDIUM"),
        ("HYD-GAC-2A", "Hyderabad", "Gachibowli", "2A", 17.4401, 78.3489, 35, 53, 48, 0.3, "LOW"),
        ("DEL-CON-1A", "Delhi", "Connaught Place", "1A", 28.6315, 77.2167, 45, 60, 85, 3.0, "HIGH"),
        ("DEL-SAK-2A", "Delhi", "Saket", "2A", 28.5244, 77.2066, 40, 58, 80, 2.0, "HIGH"),
    ]

    for z in zones_data:
        zone = Zone(
            id=str(uuid.uuid4()), zone_code=z[0], city=z[1], area_name=z[2], sub_zone=z[3],
            latitude=float(z[4]), longitude=float(z[5]),
            flood_risk_score=float(z[6]), heat_risk_score=float(z[7]), aqi_risk_score=float(z[8]),
            strike_frequency_yearly=float(z[9]), overall_risk_level=z[10],
        )
        session.add(zone)
