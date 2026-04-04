"""
LaborGuard ML - Fraud Detection Model
Isolation Forest for individual fraud anomaly detection
"""

import numpy as np
import random


class FraudModel:
    """
    Isolation Forest-style fraud detection model.
    Analyzes behavioral signals to compute fraud anomaly scores.
    """

    def __init__(self):
        self.feature_names = [
            "velocity_anomaly",
            "zone_mismatch",
            "device_risk",
            "altitude_anomaly",
            "cell_tower_mismatch",
            "motion_absence",
            "order_absence",
        ]
        # Anomaly detection thresholds
        self.contamination = 0.1  # 10% expected anomaly rate

    def compute_anomaly_score(self, features: dict) -> dict:
        """
        Compute anomaly score for a claim using Isolation Forest approach.
        More isolated = more anomalous = higher fraud score.
        """
        # Convert signals to 0-1 anomaly indicators
        signals = np.array([
            self._velocity_score(features.get("max_velocity", 0)),
            self._zone_match_score(features.get("days_in_zone", 30)),
            self._device_score(features),
            self._altitude_score(features.get("altitude_variance", 5)),
            self._cell_tower_score(features.get("gps_cell_distance", 0)),
            self._motion_score(features.get("motion_level", 0.5)),
            self._order_score(features.get("order_count", 5)),
        ])

        # Isolation Forest scoring
        # Path length in isolation tree (shorter = more anomalous)
        path_lengths = 1.0 / (1.0 + signals * 5)  # Inverted: anomalous signals have shorter paths
        avg_path = np.mean(path_lengths)

        # Normalize to 0-100 anomaly score
        n = len(signals)
        c_n = 2 * (np.log(n - 1) + 0.5772) - 2 * (n - 1) / n  # Expected path length
        anomaly_score = 2 ** (-avg_path / c_n) if c_n > 0 else 0.5

        # Scale to 0-100
        fraud_score = anomaly_score * 100

        # Boost if multiple signals are flagged
        flagged_count = sum(1 for s in signals if s > 0.5)
        if flagged_count >= 4:
            fraud_score = min(100, fraud_score * 1.3)
        elif flagged_count >= 3:
            fraud_score = min(100, fraud_score * 1.15)

        return {
            "anomaly_score": round(float(anomaly_score), 4),
            "fraud_score": round(float(fraud_score), 1),
            "signal_scores": {
                name: round(float(score), 3)
                for name, score in zip(self.feature_names, signals)
            },
            "flagged_signals": flagged_count,
            "isolation_info": {
                "avg_path_length": round(float(avg_path), 4),
                "expected_path_length": round(float(c_n), 4),
            },
        }

    def _velocity_score(self, max_velocity: float) -> float:
        """Score velocity anomaly. >120 km/h impossible for bike."""
        if max_velocity > 120:
            return 0.95
        elif max_velocity > 80:
            return 0.6
        elif max_velocity > 50:
            return 0.2
        return 0.0

    def _zone_match_score(self, days_in_zone: int) -> float:
        """Score zone history mismatch."""
        if days_in_zone <= 0:
            return 0.9
        elif days_in_zone < 3:
            return 0.7
        elif days_in_zone < 10:
            return 0.3
        return 0.0

    def _device_score(self, features: dict) -> float:
        """Score device risk indicators."""
        score = 0.0
        if features.get("is_rooted", False):
            score += 0.35
        if features.get("mock_gps", False):
            score += 0.45
        if features.get("is_emulator", False):
            score += 0.35
        return min(score, 1.0)

    def _altitude_score(self, altitude_variance: float) -> float:
        """Score altitude consistency."""
        if altitude_variance < 0.5:
            return 0.8
        elif altitude_variance < 2:
            return 0.4
        return 0.0

    def _cell_tower_score(self, distance_km: float) -> float:
        """Score GPS-to-cell-tower distance."""
        if distance_km > 15:
            return 0.9
        elif distance_km > 5:
            return 0.5
        elif distance_km > 2:
            return 0.2
        return 0.0

    def _motion_score(self, motion_level: float) -> float:
        """Score physical motion absence."""
        if motion_level < 0.1:
            return 0.85
        elif motion_level < 0.3:
            return 0.4
        return 0.0

    def _order_score(self, order_count: int) -> float:
        """Score platform order absence."""
        if order_count == 0:
            return 0.8
        elif order_count < 3:
            return 0.3
        return 0.0


# Global model instance
fraud_model = FraudModel()
