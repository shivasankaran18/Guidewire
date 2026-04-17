"""
Mock AQICN API
Simulates Air Quality Index data
"""

import random
from fastapi import APIRouter

router = APIRouter(prefix="/mock/aqicn", tags=["Mock - AQICN"])


async def get_mock_aqi(city: str = "chennai", zone_code: str = "CHN-VEL-4B"):
    """Get mock AQI data for a city/zone."""
    has_severe_aqi = random.random() < 0.1

    if has_severe_aqi:
        aqi = random.randint(400, 500)
        category = "Hazardous"
        color = "maroon"
    else:
        aqi = random.randint(50, 250)
        if aqi <= 50:
            category, color = "Good", "green"
        elif aqi <= 100:
            category, color = "Moderate", "yellow"
        elif aqi <= 150:
            category, color = "Unhealthy for Sensitive Groups", "orange"
        elif aqi <= 200:
            category, color = "Unhealthy", "red"
        else:
            category, color = "Very Unhealthy", "purple"

    return {
        "status": "ok",
        "data": {
            "aqi": aqi,
            "city": {"name": city},
            "zone_code": zone_code,
            "category": category,
            "color": color,
            "dominant_pollutant": random.choice(["pm25", "pm10", "no2", "o3"]),
            "iaqi": {
                "pm25": {"v": round(random.uniform(20, 300), 1)},
                "pm10": {"v": round(random.uniform(30, 400), 1)},
                "no2": {"v": round(random.uniform(5, 80), 1)},
                "o3": {"v": round(random.uniform(10, 120), 1)},
                "so2": {"v": round(random.uniform(2, 40), 1)},
                "co": {"v": round(random.uniform(0.5, 15), 1)},
            },
            "health_advisory": "Stay indoors. Use air purifier." if aqi > 400 else "Normal outdoor activities are fine." if aqi < 100 else "Limit prolonged outdoor exertion.",
        },
        "_source": "mock_aqicn",
    }


@router.get("/feed")
async def get_aqi(city: str = "chennai", zone_code: str = "CHN-VEL-4B"):
    """Get AQI data for a city/zone (mock only)."""
    return await get_mock_aqi(city, zone_code)
