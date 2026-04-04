"""
LaborGuard ML — Train Premium Model
XGBoost training script for dynamic weekly premium pricing
"""

import os
import pickle
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


def load_training_data():
    """Load synthetic training data."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "synthetic_workers.csv")
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        return df
    else:
        # Generate synthetic data
        from backend.ml.feature_engineering import generate_premium_features
        return generate_premium_features(n_samples=2000)


def train_premium_model():
    """Train XGBoost regression model for premium prediction."""
    print("📊 Loading training data...")
    df = load_training_data()

    feature_cols = [
        "flood_risk_3yr", "weather_forecast_risk", "aqi_forecast",
        "strike_frequency", "avg_weekly_earnings", "tenure_weeks",
        "past_claims_count",
    ]

    # Ensure all columns exist
    for col in feature_cols:
        if col not in df.columns:
            df[col] = np.random.uniform(0, 100, len(df))

    if "premium_target" not in df.columns:
        df["premium_target"] = 29 + (
            df["flood_risk_3yr"] * 0.28
            + df["weather_forecast_risk"] * 0.12
            + df["aqi_forecast"] * 0.12
            + df["strike_frequency"] * 8
            + (df["avg_weekly_earnings"] / 10000) * 10
            - (df["tenure_weeks"] / 52).clip(0, 1) * 5
            + (df["past_claims_count"] / 10).clip(0, 1) * 3
        ).clip(29, 75) + np.random.normal(0, 2, len(df))
        df["premium_target"] = df["premium_target"].clip(29, 75)

    X = df[feature_cols].values
    y = df["premium_target"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("🚀 Training XGBoost model...")
    model = XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"📈 MAE: ₹{mae:.2f}")
    print(f"📈 R² Score: {r2:.4f}")

    # Feature importance
    importance = dict(zip(feature_cols, model.feature_importances_))
    print("\n📊 Feature Importance:")
    for feat, imp in sorted(importance.items(), key=lambda x: -x[1]):
        print(f"  {feat}: {imp:.4f}")

    # Save model
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "premium_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"\n✅ Model saved to {model_path}")

    return model, {"mae": mae, "r2": r2, "feature_importance": importance}


if __name__ == "__main__":
    train_premium_model()
