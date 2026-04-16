"""
GigPulse Sentinel Trigger Monitor Service
Real-time parametric trigger monitoring for 5 trigger types
"""

import uuid
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Trigger, Zone

TRIGGER_CONFIGS = {
    "HEAVY_RAIN": {"name": "Heavy Rainfall", "api_source": "OpenWeatherMap", "threshold": 80, "unit": "mm/hr", "description": "Heavy rainfall exceeding 80mm/hr in zone"},
    "FLOOD": {"name": "Flood / Waterlogging", "api_source": "IMD Alert API", "threshold": None, "unit": "alert_level", "description": "IMD Red Alert for flooding/waterlogging"},
    "HEAT": {"name": "Severe Heat", "api_source": "OpenWeatherMap", "threshold": 43, "unit": "°C", "description": "Sustained temperature exceeding 43°C"},
    "AQI": {"name": "Severe AQI", "api_source": "AQICN API", "threshold": 400, "unit": "AQI", "description": "Air Quality Index exceeding 400 (Hazardous)"},
    "ORDER_SUSPENSION": {"name": "Platform Order Suspension", "api_source": "Zomato Mock API", "threshold": 2, "unit": "hours", "description": "Orders down for more than 2 hours in zone"},
}


class TriggerMonitor:
    @staticmethod
    async def check_triggers(db: AsyncSession, zone_code: str) -> dict:
        result = await db.execute(select(Zone).where(Zone.zone_code == zone_code))
        zone = result.scalar_one_or_none()
        if not zone:
            return {"zone_code": zone_code, "triggers": [], "error": "Zone not found"}

        active_triggers = []
        weather_data = TriggerMonitor._get_mock_weather(zone)
        aqi_data = TriggerMonitor._get_mock_aqi(zone)
        platform_data = TriggerMonitor._get_mock_platform(zone)

        if weather_data["rainfall_mm"] > TRIGGER_CONFIGS["HEAVY_RAIN"]["threshold"]:
            active_triggers.append({"type": "HEAVY_RAIN", "severity": TriggerMonitor._get_severity(weather_data["rainfall_mm"], 80, 120, 160), "value": weather_data["rainfall_mm"], "threshold": 80, "sources_agreeing": weather_data.get("sources_agreeing", 2)})
        if weather_data.get("flood_alert") == "RED":
            active_triggers.append({"type": "FLOOD", "severity": "CRITICAL", "value": "RED_ALERT", "threshold": "RED_ALERT", "sources_agreeing": 3})
        if weather_data["temperature"] > TRIGGER_CONFIGS["HEAT"]["threshold"]:
            active_triggers.append({"type": "HEAT", "severity": TriggerMonitor._get_severity(weather_data["temperature"], 43, 45, 48), "value": weather_data["temperature"], "threshold": 43, "sources_agreeing": weather_data.get("sources_agreeing", 2)})
        if aqi_data["aqi"] > TRIGGER_CONFIGS["AQI"]["threshold"]:
            active_triggers.append({"type": "AQI", "severity": TriggerMonitor._get_severity(aqi_data["aqi"], 400, 450, 500), "value": aqi_data["aqi"], "threshold": 400, "sources_agreeing": aqi_data.get("sources_agreeing", 2)})
        if platform_data.get("orders_down_hours", 0) > TRIGGER_CONFIGS["ORDER_SUSPENSION"]["threshold"]:
            active_triggers.append({"type": "ORDER_SUSPENSION", "severity": "HIGH", "value": platform_data["orders_down_hours"], "threshold": 2, "sources_agreeing": platform_data.get("sources_agreeing", 2)})

        return {"zone_code": zone_code, "city": zone.city, "area_name": zone.area_name, "checked_at": datetime.now(timezone.utc).isoformat(), "active_triggers": active_triggers, "weather": weather_data, "aqi": aqi_data, "platform": platform_data, "trigger_configs": TRIGGER_CONFIGS}

    @staticmethod
    async def fire_trigger(db: AsyncSession, zone_code: str, trigger_type: str, value: float, sources_agreeing: int = 3) -> Trigger:
        result = await db.execute(select(Zone).where(Zone.zone_code == zone_code))
        zone = result.scalar_one_or_none()
        if not zone:
            raise ValueError(f"Zone {zone_code} not found")
        config = TRIGGER_CONFIGS.get(trigger_type)
        if not config:
            raise ValueError(f"Unknown trigger type: {trigger_type}")

        severity = "HIGH"
        if isinstance(value, (int, float)) and config["threshold"]:
            severity = TriggerMonitor._get_severity(value, config["threshold"], config["threshold"] * 1.3, config["threshold"] * 1.6)
        auto_approved = sources_agreeing == 3

        trigger = Trigger(
            id=str(uuid.uuid4()), zone_id=zone.id, zone_code=zone_code,
            trigger_type=trigger_type, severity=severity,
            threshold_value=value if isinstance(value, (int, float)) else None,
            threshold_limit=config["threshold"], source_primary=config["api_source"],
            source_secondary="IMD Cross-Validation", source_tertiary="Platform Activity",
            sources_agreeing=sources_agreeing, auto_approved=auto_approved,
            raw_data={"value": value, "config": config["name"]},
            expires_at=datetime.now(timezone.utc) + timedelta(hours=6), status="ACTIVE",
        )
        db.add(trigger)
        await db.flush()
        return trigger

    @staticmethod
    async def get_active_triggers(db: AsyncSession, zone_code: str = None) -> list:
        query = select(Trigger).where(Trigger.status == "ACTIVE")
        if zone_code:
            query = query.where(Trigger.zone_code == zone_code)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def _get_severity(value, low, medium, high):
        if value >= high: return "CRITICAL"
        elif value >= medium: return "HIGH"
        elif value >= low: return "MODERATE"
        return "LOW"

    @staticmethod
    def _get_mock_weather(zone):
        flood_risk = zone.flood_risk_score / 100
        heat_risk = zone.heat_risk_score / 100
        has_rain = random.random() < flood_risk * 0.4
        has_heat = random.random() < heat_risk * 0.3
        rainfall = random.uniform(60, 150) if has_rain else 0
        temp = random.uniform(42, 48) if has_heat else random.uniform(28, 38)
        flood_alert = "RED" if rainfall > 120 else ("ORANGE" if rainfall > 80 else None)
        return {"temperature": round(temp, 1), "humidity": random.randint(60, 95), "rainfall_mm": round(rainfall, 1), "wind_speed_kmh": round(random.uniform(5, 45), 1), "flood_alert": flood_alert, "forecast_7day": "Heavy rain expected" if has_rain else "Partly cloudy", "sources_agreeing": 3 if has_rain else 2}

    @staticmethod
    def _get_mock_aqi(zone):
        has_event = random.random() < (zone.aqi_risk_score / 100) * 0.2
        aqi = random.randint(380, 500) if has_event else random.randint(80, 200)
        cat = "Hazardous" if aqi > 400 else ("Very Unhealthy" if aqi > 300 else ("Unhealthy" if aqi > 200 else ("Unhealthy for Sensitive" if aqi > 150 else ("Moderate" if aqi > 100 else "Good"))))
        return {"aqi": aqi, "category": cat, "dominant_pollutant": random.choice(["PM2.5", "PM10", "NO2", "O3"]), "sources_agreeing": 3 if has_event else 2}

    @staticmethod
    def _get_mock_platform(zone):
        has_suspension = random.random() < 0.05
        return {"platform": "Zomato", "orders_active": not has_suspension, "orders_down_hours": random.uniform(2.5, 5) if has_suspension else 0, "avg_orders_per_hour": random.randint(15, 45) if not has_suspension else 0, "zone_status": "SUSPENDED" if has_suspension else "ACTIVE", "sources_agreeing": 3 if has_suspension else 1}
