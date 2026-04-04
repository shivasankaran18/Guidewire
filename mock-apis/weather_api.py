"""
Mock OpenWeatherMap API
Simulates realistic weather data per zone
"""

import random
from fastapi import APIRouter

router = APIRouter(prefix="/mock/weather", tags=["Mock - Weather"])


@router.get("/current")
async def get_current_weather(
    lat: float = 12.9815,
    lon: float = 80.2180,
    zone_code: str = "CHN-VEL-4B",
):
    """Simulate OpenWeatherMap current weather API."""
    # Simulate based on zone risk
    is_rain_event = random.random() < 0.3
    is_heat_event = random.random() < 0.2

    temp = random.uniform(28, 38)
    if is_heat_event:
        temp = random.uniform(42, 48)

    rainfall = 0
    if is_rain_event:
        rainfall = random.uniform(60, 160)

    return {
        "coord": {"lat": lat, "lon": lon},
        "weather": [{
            "main": "Rain" if is_rain_event else "Heat" if is_heat_event else "Clouds",
            "description": "heavy intensity rain" if rainfall > 80 else "moderate rain" if rainfall > 40 else "partly cloudy",
        }],
        "main": {
            "temp": round(temp, 1),
            "feels_like": round(temp + random.uniform(1, 4), 1),
            "humidity": random.randint(55, 95),
            "pressure": random.randint(1005, 1020),
        },
        "wind": {
            "speed": round(random.uniform(2, 15), 1),
            "deg": random.randint(0, 360),
        },
        "rain": {"1h": round(rainfall, 1)} if is_rain_event else None,
        "visibility": random.randint(2000, 10000),
        "zone_code": zone_code,
        "_source": "mock_openweathermap",
    }


@router.get("/forecast")
async def get_forecast(
    lat: float = 12.9815,
    lon: float = 80.2180,
    days: int = 7,
):
    """Simulate 7-day weather forecast."""
    forecast = []
    for i in range(days):
        is_rain = random.random() < 0.25
        temp_max = random.uniform(30, 42)
        temp_min = temp_max - random.uniform(4, 8)

        forecast.append({
            "day": i + 1,
            "temp_max": round(temp_max, 1),
            "temp_min": round(temp_min, 1),
            "humidity": random.randint(55, 90),
            "rainfall_probability": round(random.uniform(0, 1), 2) if is_rain else round(random.uniform(0, 0.3), 2),
            "rainfall_mm": round(random.uniform(20, 120), 1) if is_rain else 0,
            "description": "Heavy rain expected" if is_rain else "Partly cloudy",
        })

    return {
        "coord": {"lat": lat, "lon": lon},
        "forecast": forecast,
        "_source": "mock_openweathermap",
    }
