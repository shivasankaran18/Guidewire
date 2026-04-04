# LaborGuard — Premium Pricing Model (XGBoost)

## Overview

LaborGuard uses an XGBoost gradient boosting regression model to calculate personalized weekly premiums between **₹29 and ₹75**.

## Feature Vector

| Feature | Range | Source | Importance |
|---------|-------|--------|------------|
| `flood_risk_3yr` | 0–100 | 3-year zone flood history | 28% |
| `strike_frequency` | 0–5/yr | Zone disruption history | 18% |
| `weather_forecast_risk` | 0–100 | 7-day weather forecast | 15% |
| `aqi_forecast` | 0–100 | Air quality projection | 12% |
| `avg_weekly_earnings` | ₹3K–8K | Worker's earnings DNA | 12% |
| `tenure_weeks` | 0–104 | Account age (inverse) | -8% |
| `past_claims_count` | 0–15 | Historical claim frequency | 7% |

## Model Architecture

```python
XGBRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
)
```

## Risk Pricing Logic

1. **Zone Risk** (60% weight): Flood/heat/AQI history determines base risk
2. **Behavioral Risk** (25% weight): Worker's claim history and tenure
3. **Forecast Risk** (15% weight): Next week's predicted conditions

## Non-Linear Transformation

High-risk features (> 0.5 normalized) are amplified by 1.3x, while low-risk features are dampened by 0.8x. This creates a progressive pricing curve where higher-risk workers pay proportionally more.

## Plan Tier Multipliers

| Tier | Coverage | Premium Multiplier | Max Payout |
|------|----------|-------------------|------------|
| BASIC | 1.0x earnings | 1.0x | 1x weekly avg |
| STANDARD | 1.5x earnings | 1.4x | 1.5x weekly avg |
| PREMIUM | 2.0x earnings | 1.8x | 2x weekly avg |

## SHAP-like Explainability

Each premium prediction includes feature contributions showing how each factor pushed the price up or down. Example:

```
Premium: ₹59
  flood_risk_3yr:    +₹12.4  (zone = CHN-VEL-4B, high flood area)
  strike_frequency:  +₹ 6.2  (1.5 strikes/year)
  weather_forecast:  +₹ 3.8  (rain predicted this week)
  tenure_weeks:      -₹ 4.1  (24 weeks = trusted)
  past_claims:       +₹ 1.8  (3 past claims)
```

## Model Drift Monitoring

Weekly accuracy checks:
- **Premium MAE threshold**: ₹8 (retrain if exceeded)
- **Fraud accuracy threshold**: 85% (retrain if below)
- Automated drift alerts to admin dashboard

## Training Data

- 2000 synthetic worker profiles
- Features generated from realistic Indian city disruption patterns
- Monsoon seasonality, AQI Delhi winters, Mumbai flood zone data
