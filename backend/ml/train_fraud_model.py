"""
LaborGuard ML — Train Fraud Model
Isolation Forest training script for anomaly detection
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report


def load_fraud_data():
    """Load fraud pattern data."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "fraud_patterns.csv")
    if os.path.exists(data_path):
        return pd.read_csv(data_path)
    else:
        from backend.ml.feature_engineering import generate_fraud_features
        return generate_fraud_features(n_genuine=1500, n_fraud=200)


def train_fraud_model():
    """Train Isolation Forest for fraud detection."""
    print("📊 Loading fraud data...")
    df = load_fraud_data()

    feature_cols = [
        "velocity_anomaly", "zone_mismatch", "device_risk",
        "altitude_anomaly", "cell_tower_mismatch", "motion_absence",
        "order_absence",
    ]

    for col in feature_cols:
        if col not in df.columns:
            df[col] = np.random.uniform(0, 1, len(df))

    X = df[feature_cols].values

    print("🚀 Training Isolation Forest...")
    model = IsolationForest(
        n_estimators=100,
        contamination=0.12,
        max_samples="auto",
        random_state=42,
    )
    model.fit(X)

    # Score samples
    scores = model.decision_function(X)
    predictions = model.predict(X)

    # Stats
    n_anomalies = (predictions == -1).sum()
    n_normal = (predictions == 1).sum()

    print(f"\n📊 Results:")
    print(f"  Normal: {n_normal} ({n_normal/len(X)*100:.1f}%)")
    print(f"  Anomalies: {n_anomalies} ({n_anomalies/len(X)*100:.1f}%)")

    if "is_fraud" in df.columns:
        actual = df["is_fraud"].values
        pred_binary = (predictions == -1).astype(int)
        print("\n📈 Classification Report:")
        print(classification_report(actual, pred_binary, target_names=["Genuine", "Fraud"]))

    # Save model
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "fraud_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"✅ Model saved to {model_path}")

    return model


if __name__ == "__main__":
    train_fraud_model()
