# LaborGuard — Zone Mapping Strategy

## Sub-Zone Polygon System

LaborGuard uses **500m precision sub-zone polygons** to ensure hyperlocal accuracy in disruption detection and premium pricing.

## Zone Code Format

```
{CITY}-{AREA}-{RISK_TIER}{SUB_ZONE}

Examples:
  CHN-VEL-4B  →  Chennai, Velachery, Risk Tier 4, Sub-zone B
  BLR-KOR-1A  →  Bengaluru, Koramangala, Risk Tier 1, Sub-zone A
  DEL-CON-1A  →  Delhi, Connaught Place, Risk Tier 1, Sub-zone A
```

## Supported Cities

| City | Zones | Top Risk Factors |
|------|-------|-----------------|
| **Chennai** | 8 zones | Flood (Velachery), Cyclone, Heavy Rain |
| **Bengaluru** | 4 zones | Heavy Rain, Waterlogging |
| **Mumbai** | 3 zones | Flood, Heavy Rain, Cyclone |
| **Hyderabad** | 2 zones | Heat, Moderate Rain |
| **Delhi** | 2 zones | AQI (winter), Heat (summer) |

## Zone Risk Scoring

Each zone maintains 4 risk dimensions:

| Dimension | Range | Update Frequency |
|-----------|-------|-----------------|
| `flood_risk_score` | 0–100 | Monthly (historical + forecast) |
| `heat_risk_score` | 0–100 | Weekly (seasonal + forecast) |
| `aqi_risk_score` | 0–100 | Daily (real-time + forecast) |
| `strike_frequency_yearly` | 0–5+ | Monthly (platform data) |

### Overall Risk Level
```
Weighted Score = flood * 0.4 + heat * 0.25 + aqi * 0.20 + strike * 0.15

LOW:      Score < 35
MEDIUM:   Score 35–65
HIGH:     Score 65–85
CRITICAL: Score > 85
```

## Zone Assignment

Workers select their primary delivery zone during onboarding:

1. **City Selection**: Choose from 5 supported cities
2. **Area Selection**: Choose neighborhood/area
3. **Sub-Zone Verification**: GPS confirms actual delivery area
4. **Polygon Matching**: Haversine distance to nearest zone center

## Haversine Distance

Zone matching uses the haversine formula for GPS accuracy:

```python
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)² + cos(lat1) * cos(lat2) * sin(dlon/2)²
    return R * 2 * atan2(√a, √(1-a))
```

## Cross-Validation

Trigger events are validated across 3 data sources per zone:

| Trigger | Source 1 | Source 2 | Source 3 |
|---------|----------|----------|----------|
| Heavy Rain | OpenWeatherMap | IMD Alert | Zomato zone status |
| Flood | IMD Flood Alert | OpenWeatherMap | News API |
| Heat | OpenWeatherMap | IMD | Government temp data |
| AQI | AQICN | Government CPCB | OpenWeatherMap |
| Order Suspension | Zomato API | Worker GPS | Zone order volume |

### Consensus Rules
- **3/3 agree** → Auto-approve (instant payout)
- **2/3 agree** → Soft verify (minor delay)
- **1/3 agree** → Hold for manual review
