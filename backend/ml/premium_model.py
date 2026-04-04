"""
LaborGuard ML - Premium Pricing Model
XGBoost regression for dynamic weekly premium calculation
"""

import numpy as np
import random


class PremiumModel:
    """
    XGBoost-style premium pricing model.
    Predicts personalized weekly premium based on risk features.
    Uses a simplified gradient boosting approach for demo.
    """

    def __init__(self):
        self.feature_names = [
            "flood_risk_3yr",
            "weather_forecast_risk",
            "aqi_forecast",
            "strike_frequency",
            "avg_weekly_earnings",
            "tenure_weeks",
            "past_claims_count",
        ]
        # Learned weights (simulating XGBoost feature importances)
        self.weights = np.array([0.28, 0.15, 0.12, 0.18, 0.12, -0.08, 0.07])
        self.bias = 29.0  # Base premium ₹29
        self.scale = 46.0  # Range above base (75 - 29)

    def predict(self, features: dict) -> dict:
        """
        Predict premium for given risk features.
        Returns premium amount and feature contributions.
        """
        # Normalize features
        feature_vector = np.array([
            features.get("flood_risk_3yr", 50) / 100,
            features.get("weather_forecast_risk", 50) / 100,
            features.get("aqi_forecast", 50) / 100,
            min(features.get("strike_frequency", 1) / 5, 1),
            min(features.get("avg_weekly_earnings", 5000) / 10000, 1),
            min(features.get("tenure_weeks", 0) / 52, 1),
            min(features.get("past_claims_count", 0) / 10, 1),
        ])

        # Non-linear transformation (simulating tree-based ensemble)
        transformed = np.where(
            feature_vector > 0.5,
            feature_vector * 1.3,  # High-risk amplification
            feature_vector * 0.8,   # Low-risk dampening
        )

        # Weighted prediction
        risk_score = np.dot(transformed, self.weights)
        premium = self.bias + risk_score * self.scale * 2

        # Clamp
        premium = max(29, min(75, premium))

        # Feature contributions (SHAP-like)
        contributions = {}
        for i, fname in enumerate(self.feature_names):
            contributions[fname] = round(float(transformed[i] * self.weights[i] * self.scale), 2)

        return {
            "premium": round(premium, 0),
            "risk_score": round(float(risk_score), 4),
            "feature_contributions": contributions,
            "model_info": {
                "type": "XGBoost Regression (simplified)",
                "features_used": len(self.feature_names),
                "premium_range": "₹29 - ₹75",
            },
        }

    def batch_predict(self, workers_features: list[dict]) -> list[dict]:
        """Batch premium prediction for multiple workers."""
        return [self.predict(f) for f in workers_features]

    @staticmethod
    def generate_training_data(n_samples: int = 1000) -> tuple:
        """Generate synthetic training data for the premium model."""
        X = []
        y = []

        for _ in range(n_samples):
            flood_risk = random.uniform(0, 100)
            weather = random.uniform(0, 100)
            aqi = random.uniform(0, 100)
            strikes = random.uniform(0, 5)
            earnings = random.uniform(3000, 8000)
            tenure = random.randint(0, 104)
            claims = random.randint(0, 15)

            features = [flood_risk, weather, aqi, strikes, earnings, tenure, claims]

            # Synthetic label (what premium should be)
            risk = (
                flood_risk * 0.3
                + weather * 0.15
                + aqi * 0.12
                + strikes * 15
                + (earnings / 8000) * 10
                - min(tenure / 52, 1) * 8
                + (claims / 10) * 5
            )
            premium = 29 + (risk / 100) * 46
            premium = max(29, min(75, premium + random.gauss(0, 3)))

            X.append(features)
            y.append(premium)

        return np.array(X), np.array(y)


# Global model instance
premium_model = PremiumModel()
