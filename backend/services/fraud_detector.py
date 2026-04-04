"""
LaborGuard Fraud Detector Service
7-signal fraud risk scoring using Isolation Forest approach
"""

import random
import math
from dataclasses import dataclass


@dataclass
class FraudSignal:
    """Individual fraud detection signal."""
    name: str
    score: float  # 0-100
    description: str
    is_flagged: bool


class FraudDetector:
    """
    Multi-signal fraud detection engine.
    Analyzes 7 independent signals to build a Fraud Risk Score (0-100).
    """

    # Signal weights for composite score
    SIGNAL_WEIGHTS = {
        "movement_velocity": 0.15,
        "location_history": 0.18,
        "device_fingerprint": 0.15,
        "gps_altitude": 0.10,
        "cell_tower_match": 0.15,
        "accelerometer": 0.12,
        "platform_orders": 0.15,
    }

    # Fraud tier thresholds
    TIERS = {
        "GREEN": (0, 30),
        "AMBER": (31, 60),
        "RED": (61, 100),
    }

    @staticmethod
    def analyze_claim(
        worker_data: dict,
        location_data: dict = None,
        device_data: dict = None,
        platform_data: dict = None,
    ) -> dict:
        """
        Run full fraud analysis on a claim.
        Returns fraud score, tier, and individual signal breakdown.
        """
        signals = []

        # 1. Movement Velocity Check
        velocity_signal = FraudDetector._check_movement_velocity(
            location_data or {}
        )
        signals.append(velocity_signal)

        # 2. Location History Match
        history_signal = FraudDetector._check_location_history(
            worker_data, location_data or {}
        )
        signals.append(history_signal)

        # 3. Device Fingerprint Check
        device_signal = FraudDetector._check_device_fingerprint(
            device_data or {}
        )
        signals.append(device_signal)

        # 4. GPS Altitude Consistency
        altitude_signal = FraudDetector._check_gps_altitude(
            location_data or {}
        )
        signals.append(altitude_signal)

        # 5. Cell Tower vs GPS Match
        cell_signal = FraudDetector._check_cell_tower_match(
            location_data or {}
        )
        signals.append(cell_signal)

        # 6. Accelerometer / Gyroscope
        accel_signal = FraudDetector._check_accelerometer(
            device_data or {}
        )
        signals.append(accel_signal)

        # 7. Platform Order Logs
        order_signal = FraudDetector._check_platform_orders(
            platform_data or {}
        )
        signals.append(order_signal)

        # Compute weighted fraud score
        fraud_score = FraudDetector._compute_fraud_score(signals)

        # Determine tier
        fraud_tier = "GREEN"
        for tier, (low, high) in FraudDetector.TIERS.items():
            if low <= fraud_score <= high:
                fraud_tier = tier
                break

        # Determine verification method
        verification = {
            "GREEN": "AUTO",
            "AMBER": "SOFT_VERIFY",
            "RED": "MANUAL_REVIEW",
        }

        # Confidence score (inverse of fraud score, shown to worker)
        confidence = max(0, 100 - fraud_score)

        return {
            "fraud_score": round(fraud_score, 1),
            "fraud_tier": fraud_tier,
            "confidence_score": round(confidence, 1),
            "verification_method": verification[fraud_tier],
            "signals": {s.name: {
                "score": s.score,
                "flagged": s.is_flagged,
                "description": s.description,
            } for s in signals},
            "flagged_signals": [s.name for s in signals if s.is_flagged],
            "recommendation": FraudDetector._get_recommendation(fraud_tier, fraud_score),
        }

    @staticmethod
    def _check_movement_velocity(location_data: dict) -> FraudSignal:
        """Check speed between consecutive GPS pings. >120 km/h = impossible for bike."""
        velocity = location_data.get("velocity_kmh", 0)
        max_velocity = location_data.get("max_velocity_kmh", 0)

        if max_velocity > 120:
            return FraudSignal(
                name="movement_velocity",
                score=85,
                description=f"Impossible velocity detected: {max_velocity:.0f} km/h between pings",
                is_flagged=True,
            )
        elif max_velocity > 80:
            return FraudSignal(
                name="movement_velocity",
                score=45,
                description=f"High velocity: {max_velocity:.0f} km/h (unusual for delivery bike)",
                is_flagged=True,
            )
        else:
            return FraudSignal(
                name="movement_velocity",
                score=max(0, velocity * 0.3),
                description=f"Normal movement velocity: {velocity:.0f} km/h",
                is_flagged=False,
            )

    @staticmethod
    def _check_location_history(worker_data: dict, location_data: dict) -> FraudSignal:
        """Does claimed zone match last 30 days of delivery routes?"""
        zone_match = location_data.get("zone_match_30d", True)
        days_in_zone = location_data.get("days_in_zone_30d", 20)

        if not zone_match or days_in_zone < 3:
            return FraudSignal(
                name="location_history",
                score=70,
                description=f"Worker has only {days_in_zone} days in this zone (last 30d). Never delivered here before.",
                is_flagged=True,
            )
        elif days_in_zone < 10:
            return FraudSignal(
                name="location_history",
                score=35,
                description=f"Worker has {days_in_zone} days in this zone (last 30d). Occasional presence.",
                is_flagged=False,
            )
        else:
            return FraudSignal(
                name="location_history",
                score=5,
                description=f"Worker regularly delivers in this zone ({days_in_zone}/30 days)",
                is_flagged=False,
            )

    @staticmethod
    def _check_device_fingerprint(device_data: dict) -> FraudSignal:
        """Check for rooted device, mock GPS app, or emulator."""
        is_rooted = device_data.get("is_rooted", False)
        has_mock_gps = device_data.get("mock_gps_detected", False)
        is_emulator = device_data.get("is_emulator", False)

        score = 0
        flags = []
        if is_rooted:
            score += 30
            flags.append("rooted device")
        if has_mock_gps:
            score += 40
            flags.append("mock GPS app detected")
        if is_emulator:
            score += 30
            flags.append("running on emulator")

        if flags:
            return FraudSignal(
                name="device_fingerprint",
                score=min(score, 100),
                description=f"Device anomalies: {', '.join(flags)}",
                is_flagged=True,
            )
        return FraudSignal(
            name="device_fingerprint",
            score=0,
            description="Device fingerprint clean — no spoofing indicators",
            is_flagged=False,
        )

    @staticmethod
    def _check_gps_altitude(location_data: dict) -> FraudSignal:
        """Check altitude variance. Static altitude = phone sitting still."""
        altitude_variance = location_data.get("altitude_variance", 5.0)

        if altitude_variance < 0.5:
            return FraudSignal(
                name="gps_altitude",
                score=60,
                description=f"Near-zero altitude variance ({altitude_variance:.1f}m) — phone may be stationary",
                is_flagged=True,
            )
        elif altitude_variance < 2.0:
            return FraudSignal(
                name="gps_altitude",
                score=30,
                description=f"Low altitude variance ({altitude_variance:.1f}m) — limited movement",
                is_flagged=False,
            )
        return FraudSignal(
            name="gps_altitude",
            score=0,
            description=f"Normal altitude variance ({altitude_variance:.1f}m) — active movement",
            is_flagged=False,
        )

    @staticmethod
    def _check_cell_tower_match(location_data: dict) -> FraudSignal:
        """Check if cell tower location matches GPS coordinates."""
        gps_cell_distance = location_data.get("gps_cell_distance_km", 0)

        if gps_cell_distance > 15:
            return FraudSignal(
                name="cell_tower_match",
                score=80,
                description=f"GPS-Cell Tower mismatch: {gps_cell_distance:.1f}km — likely GPS spoofing",
                is_flagged=True,
            )
        elif gps_cell_distance > 5:
            return FraudSignal(
                name="cell_tower_match",
                score=35,
                description=f"Moderate GPS-Cell distance: {gps_cell_distance:.1f}km",
                is_flagged=True,
            )
        return FraudSignal(
            name="cell_tower_match",
            score=0,
            description=f"GPS matches cell tower ({gps_cell_distance:.1f}km)",
            is_flagged=False,
        )

    @staticmethod
    def _check_accelerometer(device_data: dict) -> FraudSignal:
        """Check physical motion from accelerometer/gyroscope."""
        motion_level = device_data.get("motion_level", 0.5)  # 0-1

        if motion_level < 0.1:
            return FraudSignal(
                name="accelerometer",
                score=65,
                description="Zero physical motion during claimed active delivery — phone stationary",
                is_flagged=True,
            )
        elif motion_level < 0.3:
            return FraudSignal(
                name="accelerometer",
                score=30,
                description="Very low physical motion — limited activity",
                is_flagged=False,
            )
        return FraudSignal(
            name="accelerometer",
            score=0,
            description=f"Normal physical motion detected (level: {motion_level:.2f})",
            is_flagged=False,
        )

    @staticmethod
    def _check_platform_orders(platform_data: dict) -> FraudSignal:
        """Check if platform shows order activity in claimed zone."""
        has_orders = platform_data.get("has_orders_in_zone", True)
        order_count = platform_data.get("order_count_today", 5)

        if not has_orders or order_count == 0:
            return FraudSignal(
                name="platform_orders",
                score=70,
                description="No order activity on platform in claimed zone — no physical presence confirmed",
                is_flagged=True,
            )
        elif order_count < 3:
            return FraudSignal(
                name="platform_orders",
                score=20,
                description=f"Low order activity ({order_count} orders) in claimed zone",
                is_flagged=False,
            )
        return FraudSignal(
            name="platform_orders",
            score=0,
            description=f"Active order history ({order_count} orders) confirms presence",
            is_flagged=False,
        )

    @staticmethod
    def _compute_fraud_score(signals: list[FraudSignal]) -> float:
        """Compute weighted composite fraud score."""
        weight_keys = list(FraudDetector.SIGNAL_WEIGHTS.keys())
        total = 0
        for signal in signals:
            weight = FraudDetector.SIGNAL_WEIGHTS.get(signal.name, 0.1)
            total += signal.score * weight
        return min(100, total)

    @staticmethod
    def _get_recommendation(tier: str, score: float) -> str:
        """Get human-readable recommendation based on fraud analysis."""
        if tier == "GREEN":
            return "Auto-approve. Instant UPI payout recommended."
        elif tier == "AMBER":
            return "Soft verification required. One-tap confirm + order log cross-check."
        else:
            return "Payout held. Manual review required within 2 hours. Notify worker with clear explanation."

    @staticmethod
    def generate_demo_analysis(is_genuine: bool = True) -> dict:
        """Generate a realistic demo fraud analysis for presentation."""
        if is_genuine:
            worker_data = {"tenure_weeks": 24}
            location_data = {
                "velocity_kmh": 25,
                "max_velocity_kmh": 45,
                "zone_match_30d": True,
                "days_in_zone_30d": 22,
                "altitude_variance": 8.5,
                "gps_cell_distance_km": 0.8,
            }
            device_data = {
                "is_rooted": False,
                "mock_gps_detected": False,
                "is_emulator": False,
                "motion_level": 0.72,
            }
            platform_data = {
                "has_orders_in_zone": True,
                "order_count_today": 8,
            }
        else:
            worker_data = {"tenure_weeks": 2}
            location_data = {
                "velocity_kmh": 0,
                "max_velocity_kmh": 180,
                "zone_match_30d": False,
                "days_in_zone_30d": 0,
                "altitude_variance": 0.2,
                "gps_cell_distance_km": 25,
            }
            device_data = {
                "is_rooted": True,
                "mock_gps_detected": True,
                "is_emulator": False,
                "motion_level": 0.02,
            }
            platform_data = {
                "has_orders_in_zone": False,
                "order_count_today": 0,
            }

        return FraudDetector.analyze_claim(
            worker_data, location_data, device_data, platform_data
        )
