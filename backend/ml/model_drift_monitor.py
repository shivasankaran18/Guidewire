"""
LaborGuard ML — Model Drift Monitor
Weekly accuracy check for premium and fraud models
"""

import os
import pickle
import numpy as np
from datetime import datetime, timezone


class ModelDriftMonitor:
    """
    Monitors model performance over time.
    Flags drift when accuracy degrades beyond thresholds.
    """

    PREMIUM_MAE_THRESHOLD = 8.0    # ₹8 acceptable MAE
    FRAUD_ACCURACY_THRESHOLD = 0.85  # 85% accuracy minimum

    def __init__(self):
        self.checks = []

    def check_premium_model(self, predictions: np.ndarray, actuals: np.ndarray) -> dict:
        """Check premium model accuracy."""
        mae = np.mean(np.abs(predictions - actuals))
        mape = np.mean(np.abs((actuals - predictions) / np.maximum(actuals, 1))) * 100

        is_drifted = mae > self.PREMIUM_MAE_THRESHOLD

        result = {
            "model": "premium_xgboost",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mae": round(float(mae), 2),
            "mape": round(float(mape), 2),
            "threshold": self.PREMIUM_MAE_THRESHOLD,
            "is_drifted": is_drifted,
            "recommendation": "Retrain model with recent data" if is_drifted else "Model performing within bounds",
            "samples_checked": len(predictions),
        }
        self.checks.append(result)
        return result

    def check_fraud_model(self, predictions: np.ndarray, actuals: np.ndarray) -> dict:
        """Check fraud model accuracy."""
        accuracy = np.mean(predictions == actuals)
        true_positives = np.sum((predictions == 1) & (actuals == 1))
        false_positives = np.sum((predictions == 1) & (actuals == 0))
        false_negatives = np.sum((predictions == 0) & (actuals == 1))

        precision = true_positives / max(true_positives + false_positives, 1)
        recall = true_positives / max(true_positives + false_negatives, 1)

        is_drifted = accuracy < self.FRAUD_ACCURACY_THRESHOLD

        result = {
            "model": "fraud_isolation_forest",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "accuracy": round(float(accuracy), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "threshold": self.FRAUD_ACCURACY_THRESHOLD,
            "is_drifted": is_drifted,
            "recommendation": "Retrain with recent fraud patterns" if is_drifted else "Model performing within bounds",
            "samples_checked": len(predictions),
            "false_positive_rate": round(float(false_positives / max(len(predictions), 1)), 4),
        }
        self.checks.append(result)
        return result

    def get_drift_report(self) -> dict:
        """Generate drift monitoring report."""
        return {
            "checks_performed": len(self.checks),
            "drifted_models": [c for c in self.checks if c.get("is_drifted")],
            "healthy_models": [c for c in self.checks if not c.get("is_drifted")],
            "last_check": self.checks[-1] if self.checks else None,
        }


# Global monitor instance
drift_monitor = ModelDriftMonitor()
