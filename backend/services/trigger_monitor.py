"""
LaborGuard Trigger Monitor Service
Real-time parametric trigger monitoring for 5 trigger types
"""

import uuid
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Trigger, Zone


# Trigger type configurations
TRIGGER_CONFIGS = {
    "HEAVY_RAIN": {
        "name": "Heavy Rainfall",
        "api_source": "OpenWeatherMap",
        "threshold": 80,  # mm/hr
        "unit": "mm/hr",
        "description": "Heavy rainfall exceeding 80mm/hr in zone",
    },
    "FLOOD": {
        "name": "Flood / Waterlogging",
        "api_source": "IMD Alert API",
        "threshold": None,  # Red alert = trigger
        "unit": "alert_level",
        "description": "IMD Red Alert for flooding/waterlogging",
    },
    "HEAT": {
        "name": "Severe Heat",
        "api_source": "OpenWeatherMap",
        "threshold": 43,  # °C
        "unit": "°C",
        "description": "Sustained temperature exceeding 43°C",
    },
    "AQI": {
        "name": "Severe AQI",
        "api_source": "AQICN API",
        "threshold": 400,  # AQI value
        "unit": "AQI",
        "description": "Air Quality Index exceeding 400 (Hazardous)",
    },
    "ORDER_SUSPENSION": {
        "name": "Platform Order Suspension",
        "api_source": "Zomato Mock API",
        "threshold": 2,  # hours
        "unit": "hours",
        "description": "Orders down for more than 2 hours in zone",
    },
}


class TriggerMonitor:
    """
    Real-time parametric trigger monitoring.
    Triple-source cross-validation before auto-approval.
    """

    @staticmethod
    async def check_triggers(
        db: AsyncSession,
        zone_code: str,
    ) -> dict:
        """Check all trigger conditions for a zone."""
        # Get zone
        result = await db.execute(
            select(Zone).where(Zone.zone_code == zone_code)
        )
        zone = result.scalar_one_or_none()

        if not zone:
            return {"zone_code": zone_code, "triggers": [], "error": "Zone not found"}

        # Check each trigger type using mock data
        active_triggers = []
        weather_data = TriggerMonitor._get_mock_weather(zone)
        aqi_data = TriggerMonitor._get_mock_aqi(zone)
        platform_data = TriggerMonitor._get_mock_platform(zone)

        # Heavy Rainfall
        if weather_data["rainfall_mm"] > TRIGGER_CONFIGS["HEAVY_RAIN"]["threshold"]:
            active_triggers.append({
                "type": "HEAVY_RAIN",
                "severity": TriggerMonitor._get_severity(weather_data["rainfall_mm"], 80, 120, 160),
                "value": weather_data["rainfall_mm"],
                "threshold": 80,
                "sources_agreeing": weather_data.get("sources_agreeing", 2),
            })

        # Flood
        if weather_data.get("flood_alert") == "RED":
            active_triggers.append({
                "type": "FLOOD",
                "severity": "CRITICAL",
                "value": "RED_ALERT",
                "threshold": "RED_ALERT",
                "sources_agreeing": 3,
            })

        # Severe Heat
        if weather_data["temperature"] > TRIGGER_CONFIGS["HEAT"]["threshold"]:
            active_triggers.append({
                "type": "HEAT",
                "severity": TriggerMonitor._get_severity(weather_data["temperature"], 43, 45, 48),
                "value": weather_data["temperature"],
                "threshold": 43,
                "sources_agreeing": weather_data.get("sources_agreeing", 2),
            })

        # AQI
        if aqi_data["aqi"] > TRIGGER_CONFIGS["AQI"]["threshold"]:
            active_triggers.append({
                "type": "AQI",
                "severity": TriggerMonitor._get_severity(aqi_data["aqi"], 400, 450, 500),
                "value": aqi_data["aqi"],
                "threshold": 400,
                "sources_agreeing": aqi_data.get("sources_agreeing", 2),
            })

        # Order Suspension
        if platform_data.get("orders_down_hours", 0) > TRIGGER_CONFIGS["ORDER_SUSPENSION"]["threshold"]:
            active_triggers.append({
                "type": "ORDER_SUSPENSION",
                "severity": "HIGH",
                "value": platform_data["orders_down_hours"],
                "threshold": 2,
                "sources_agreeing": platform_data.get("sources_agreeing", 2),
            })

        return {
            "zone_code": zone_code,
            "city": zone.city,
            "area_name": zone.area_name,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "active_triggers": active_triggers,
            "weather": weather_data,
            "aqi": aqi_data,
            "platform": platform_data,
            "trigger_configs": TRIGGER_CONFIGS,
        }

    @staticmethod
    async def fire_trigger(
        db: AsyncSession,
        zone_code: str,
        trigger_type: str,
        value: float,
        sources_agreeing: int = 3,
    ) -> Trigger:
        """Fire a parametric trigger and save to database."""
        result = await db.execute(
            select(Zone).where(Zone.zone_code == zone_code)
        )
        zone = result.scalar_one_or_none()
        if not zone:
            raise ValueError(f"Zone {zone_code} not found")

        config = TRIGGER_CONFIGS.get(trigger_type)
        if not config:
            raise ValueError(f"Unknown trigger type: {trigger_type}")

        severity = "HIGH"
        if isinstance(value, (int, float)) and config["threshold"]:
            severity = TriggerMonitor._get_severity(
                value, config["threshold"],
                config["threshold"] * 1.3,
                config["threshold"] * 1.6,
            )

        auto_approved = sources_agreeing == 3

        trigger = Trigger(
            id=str(uuid.uuid4()),
            zone_id=zone.id,
            zone_code=zone_code,
            trigger_type=trigger_type,
            severity=severity,
            threshold_value=value if isinstance(value, (int, float)) else None,
            threshold_limit=config["threshold"],
            source_primary=config["api_source"],
            source_secondary="IMD Cross-Validation",
            source_tertiary="Platform Activity",
            sources_agreeing=sources_agreeing,
            auto_approved=auto_approved,
            raw_data={"value": value, "config": config["name"]},
            expires_at=datetime.now(timezone.utc) + timedelta(hours=6),
            status="ACTIVE",
        )

        db.add(trigger)
        await db.flush()
        return trigger

    @staticmethod
    async def get_active_triggers(
        db: AsyncSession,
        zone_code: str = None,
    ) -> list[Trigger]:
        """Get all active triggers, optionally filtered by zone."""
        query = select(Trigger).where(
            Trigger.status == "ACTIVE",
        )
        if zone_code:
            query = query.where(Trigger.zone_code == zone_code)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def _get_severity(value: float, low: float, medium: float, high: float) -> str:
        """Determine severity from value thresholds."""
        if value >= high:
            return "CRITICAL"
        elif value >= medium:
            return "HIGH"
        elif value >= low:
            return "MODERATE"
        return "LOW"

    @staticmethod
    def _get_mock_weather(zone: Zone) -> dict:
        """Generate realistic mock weather data for a zone."""
        # Simulate based on zone risk
        flood_risk = zone.flood_risk_score / 100
        heat_risk = zone.heat_risk_score / 100

        # Higher risk zones are more likely to have active weather events
        has_rain_event = random.random() < flood_risk * 0.4
        has_heat_event = random.random() < heat_risk * 0.3

        rainfall = 0
        if has_rain_event:
            rainfall = random.uniform(60, 150)

        temperature = random.uniform(28, 38)
        if has_heat_event:
            temperature = random.uniform(42, 48)

        flood_alert = None
        if rainfall > 120:
            flood_alert = "RED"
        elif rainfall > 80:
            flood_alert = "ORANGE"

        return {
            "temperature": round(temperature, 1),
            "humidity": random.randint(60, 95),
            "rainfall_mm": round(rainfall, 1),
            "wind_speed_kmh": round(random.uniform(5, 45), 1),
            "flood_alert": flood_alert,
            "forecast_7day": "Heavy rain expected" if has_rain_event else "Partly cloudy",
            "sources_agreeing": 3 if has_rain_event else 2,
        }

    @staticmethod
    def _get_mock_aqi(zone: Zone) -> dict:
        """Generate mock AQI data."""
        aqi_risk = zone.aqi_risk_score / 100
        has_aqi_event = random.random() < aqi_risk * 0.2

        aqi = random.randint(80, 200)
        if has_aqi_event:
            aqi = random.randint(380, 500)

        category = "Good"
        if aqi > 400:
            category = "Hazardous"
        elif aqi > 300:
            category = "Very Unhealthy"
        elif aqi > 200:
            category = "Unhealthy"
        elif aqi > 150:
            category = "Unhealthy for Sensitive"
        elif aqi > 100:
            category = "Moderate"

        return {
            "aqi": aqi,
            "category": category,
            "dominant_pollutant": random.choice(["PM2.5", "PM10", "NO2", "O3"]),
            "sources_agreeing": 3 if has_aqi_event else 2,
        }

    @staticmethod
    def _get_mock_platform(zone: Zone) -> dict:
        """Generate mock platform order status."""
        has_suspension = random.random() < 0.05  # 5% chance

        return {
            "platform": "Zomato",
            "orders_active": not has_suspension,
            "orders_down_hours": random.uniform(2.5, 5) if has_suspension else 0,
            "avg_orders_per_hour": random.randint(15, 45) if not has_suspension else 0,
            "zone_status": "SUSPENDED" if has_suspension else "ACTIVE",
            "sources_agreeing": 3 if has_suspension else 1,
        }
