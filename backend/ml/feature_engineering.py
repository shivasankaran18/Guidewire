"""
LaborGuard ML — Feature Engineering
Feature prep for both premium and fraud models
"""

import numpy as np
import pandas as pd
import random


def generate_premium_features(n_samples: int = 2000) -> pd.DataFrame:
    """Generate synthetic feature data for premium model training."""
    data = []
    for _ in range(n_samples):
        flood_risk = random.uniform(0, 100)
        weather = random.uniform(0, 100)
        aqi = random.uniform(0, 100)
        strikes = random.uniform(0, 5)
        earnings = random.uniform(3000, 8000)
        tenure = random.randint(0, 104)
        claims = random.randint(0, 15)

        # Target premium
        risk = (
            flood_risk * 0.28
            + weather * 0.15
            + aqi * 0.12
            + strikes * 9
            + (earnings / 8000) * 8
            - min(tenure / 52, 1) * 6
            + (claims / 10) * 4
        )
        premium = 29 + (risk / 100) * 46
        premium = max(29, min(75, premium + random.gauss(0, 2.5)))

        data.append({
            "flood_risk_3yr": round(flood_risk, 2),
            "weather_forecast_risk": round(weather, 2),
            "aqi_forecast": round(aqi, 2),
            "strike_frequency": round(strikes, 2),
            "avg_weekly_earnings": round(earnings, 2),
            "tenure_weeks": tenure,
            "past_claims_count": claims,
            "premium_target": round(premium, 2),
        })

    return pd.DataFrame(data)


def generate_fraud_features(n_genuine: int = 1500, n_fraud: int = 200) -> pd.DataFrame:
    """Generate synthetic fraud detection training data."""
    data = []

    # Genuine workers
    for _ in range(n_genuine):
        data.append({
            "velocity_anomaly": round(random.uniform(0, 0.3), 3),
            "zone_mismatch": round(random.uniform(0, 0.2), 3),
            "device_risk": round(random.uniform(0, 0.1), 3),
            "altitude_anomaly": round(random.uniform(0, 0.25), 3),
            "cell_tower_mismatch": round(random.uniform(0, 0.15), 3),
            "motion_absence": round(random.uniform(0, 0.2), 3),
            "order_absence": round(random.uniform(0, 0.15), 3),
            "is_fraud": 0,
        })

    # Fraudulent workers
    for _ in range(n_fraud):
        data.append({
            "velocity_anomaly": round(random.uniform(0.5, 1.0), 3),
            "zone_mismatch": round(random.uniform(0.4, 1.0), 3),
            "device_risk": round(random.uniform(0.3, 1.0), 3),
            "altitude_anomaly": round(random.uniform(0.5, 1.0), 3),
            "cell_tower_mismatch": round(random.uniform(0.4, 1.0), 3),
            "motion_absence": round(random.uniform(0.5, 1.0), 3),
            "order_absence": round(random.uniform(0.4, 1.0), 3),
            "is_fraud": 1,
        })

    random.shuffle(data)
    return pd.DataFrame(data)


def generate_zone_risk_history(n_zones: int = 20, n_weeks: int = 52) -> pd.DataFrame:
    """Generate historical zone risk data."""
    zones = [
        "CHN-VEL-4B", "CHN-VEL-4A", "CHN-ANN-2A", "CHN-ANN-2B",
        "CHN-TNR-1A", "CHN-ADY-3A", "CHN-MYL-5A", "CHN-SHN-6A",
        "BLR-KOR-1A", "BLR-IND-2A", "BLR-WHT-3A", "BLR-HSR-4A",
        "MUM-AND-1A", "MUM-BAN-2A", "MUM-DAD-3A",
        "HYD-HIB-1A", "HYD-GAC-2A",
        "DEL-CON-1A", "DEL-SAK-2A",
    ][:n_zones]

    data = []
    for zone in zones:
        base_flood = random.uniform(20, 90)
        base_heat = random.uniform(20, 70)
        base_aqi = random.uniform(30, 80)

        for week in range(n_weeks):
            # Seasonal variation
            season_factor = 1 + 0.3 * np.sin(2 * np.pi * week / 52)

            data.append({
                "zone_code": zone,
                "week": week + 1,
                "flood_events": max(0, int(base_flood / 30 * season_factor + random.gauss(0, 1))),
                "heat_events": max(0, int(base_heat / 40 * (2 - season_factor) + random.gauss(0, 0.5))),
                "aqi_events": max(0, int(base_aqi / 50 + random.gauss(0, 0.5))),
                "flood_risk_score": round(min(100, base_flood * season_factor + random.gauss(0, 5)), 2),
                "heat_risk_score": round(min(100, base_heat * (2 - season_factor) + random.gauss(0, 5)), 2),
                "aqi_risk_score": round(min(100, base_aqi + random.gauss(0, 8)), 2),
                "total_claims": random.randint(0, 15),
                "total_payouts_inr": round(random.uniform(0, 5000), 2),
            })

    return pd.DataFrame(data)


if __name__ == "__main__":
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

    print("Generating synthetic workers...")
    df_workers = generate_premium_features(2000)
    df_workers.to_csv(os.path.join(data_dir, "synthetic_workers.csv"), index=False)
    print(f"  → {len(df_workers)} records saved")

    print("Generating fraud patterns...")
    df_fraud = generate_fraud_features(1500, 200)
    df_fraud.to_csv(os.path.join(data_dir, "fraud_patterns.csv"), index=False)
    print(f"  → {len(df_fraud)} records saved")

    print("Generating zone risk history...")
    df_zones = generate_zone_risk_history()
    df_zones.to_csv(os.path.join(data_dir, "zone_risk_history.csv"), index=False)
    print(f"  → {len(df_zones)} records saved")

    print("✅ All data files generated!")
