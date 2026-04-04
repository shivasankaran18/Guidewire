"""
LaborGuard Zone Engine Service
Zone-based risk assessment & sub-zone mapping at 500m polygon precision
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import Zone
import math


# Zone risk thresholds
RISK_THRESHOLDS = {
    "LOW": (0, 30),
    "MEDIUM": (30, 60),
    "HIGH": (60, 80),
    "CRITICAL": (80, 100),
}


class ZoneEngine:
    """Zone-based risk assessment engine."""

    @staticmethod
    async def get_zone_by_code(db: AsyncSession, zone_code: str) -> Zone | None:
        """Get zone by its code."""
        result = await db.execute(
            select(Zone).where(Zone.zone_code == zone_code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_zones_by_city(db: AsyncSession, city: str) -> list[Zone]:
        """Get all zones in a city."""
        result = await db.execute(
            select(Zone).where(Zone.city == city, Zone.is_active == True)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_all_zones(db: AsyncSession) -> list[Zone]:
        """Get all active zones."""
        result = await db.execute(
            select(Zone).where(Zone.is_active == True)
        )
        return list(result.scalars().all())

    @staticmethod
    def calculate_overall_risk(zone: Zone) -> dict:
        """Calculate overall risk score and level for a zone."""
        # Weighted risk calculation
        weights = {
            "flood": 0.35,
            "heat": 0.20,
            "aqi": 0.20,
            "strike": 0.25,
        }

        overall_score = (
            zone.flood_risk_score * weights["flood"]
            + zone.heat_risk_score * weights["heat"]
            + zone.aqi_risk_score * weights["aqi"]
            + min(zone.strike_frequency_yearly * 20, 100) * weights["strike"]
        )

        risk_level = "LOW"
        for level, (low, high) in RISK_THRESHOLDS.items():
            if low <= overall_score < high:
                risk_level = level
                break
        if overall_score >= 80:
            risk_level = "CRITICAL"

        return {
            "overall_score": round(overall_score, 2),
            "risk_level": risk_level,
            "breakdown": {
                "flood_risk": round(zone.flood_risk_score, 2),
                "heat_risk": round(zone.heat_risk_score, 2),
                "aqi_risk": round(zone.aqi_risk_score, 2),
                "strike_risk": round(min(zone.strike_frequency_yearly * 20, 100), 2),
            },
            "weights": weights,
        }

    @staticmethod
    def get_nearby_zones(
        zones: list[Zone],
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
    ) -> list[dict]:
        """Find zones near a geographic point."""
        nearby = []
        for zone in zones:
            distance = ZoneEngine._haversine(
                latitude, longitude, zone.latitude, zone.longitude
            )
            if distance <= radius_km:
                nearby.append({
                    "zone": zone,
                    "distance_km": round(distance, 2),
                })
        nearby.sort(key=lambda x: x["distance_km"])
        return nearby

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coordinates in km."""
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    async def get_zone_risk_for_premium(
        db: AsyncSession,
        zone_code: str,
    ) -> dict:
        """Get zone risk factors formatted for premium calculation."""
        zone = await ZoneEngine.get_zone_by_code(db, zone_code)
        if not zone:
            return {
                "zone_found": False,
                "flood_risk_3yr": 50.0,
                "heat_risk": 50.0,
                "aqi_risk": 50.0,
                "strike_frequency": 1.0,
            }

        risk = ZoneEngine.calculate_overall_risk(zone)
        return {
            "zone_found": True,
            "zone_code": zone.zone_code,
            "city": zone.city,
            "area_name": zone.area_name,
            "flood_risk_3yr": zone.flood_risk_score,
            "heat_risk": zone.heat_risk_score,
            "aqi_risk": zone.aqi_risk_score,
            "strike_frequency": zone.strike_frequency_yearly,
            "overall_risk_score": risk["overall_score"],
            "overall_risk_level": risk["risk_level"],
        }
