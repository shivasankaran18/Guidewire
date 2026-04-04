"""
Mock IMD (India Meteorological Department) Alert API
Simulates flood/cyclone alerts
"""

import random
from fastapi import APIRouter

router = APIRouter(prefix="/mock/imd", tags=["Mock - IMD"])


@router.get("/alerts")
async def get_alerts(zone_code: str = "CHN-VEL-4B", city: str = "Chennai"):
    """Get IMD alerts for a zone/city."""
    # Simulate alert probability
    has_alert = random.random() < 0.2

    if not has_alert:
        return {
            "zone_code": zone_code,
            "city": city,
            "alerts": [],
            "overall_status": "NORMAL",
            "_source": "mock_imd",
        }

    alert_level = random.choice(["ORANGE", "ORANGE", "RED"])
    alert_types = random.choice([
        "Heavy Rainfall Warning",
        "Flood Warning",
        "Cyclone Warning",
        "Severe Waterlogging Alert",
    ])

    return {
        "zone_code": zone_code,
        "city": city,
        "alerts": [{
            "type": alert_types,
            "level": alert_level,
            "description": f"{alert_level} alert: {alert_types} for {city} region",
            "valid_from": "2026-04-01T00:00:00Z",
            "valid_until": "2026-04-02T00:00:00Z",
            "affected_areas": [zone_code],
            "recommended_action": "Avoid outdoor activities" if alert_level == "RED" else "Exercise caution",
        }],
        "overall_status": alert_level,
        "_source": "mock_imd",
    }


@router.get("/flood-status")
async def get_flood_status(zone_code: str = "CHN-VEL-4B"):
    """Get flood/waterlogging status for a zone."""
    is_flood = random.random() < 0.15

    return {
        "zone_code": zone_code,
        "flood_status": "RED" if is_flood else "NORMAL",
        "water_level_cm": random.randint(30, 90) if is_flood else random.randint(0, 10),
        "drainage_status": "OVERWHELMED" if is_flood else "NORMAL",
        "road_accessibility": "BLOCKED" if is_flood else "CLEAR",
        "_source": "mock_imd",
    }
