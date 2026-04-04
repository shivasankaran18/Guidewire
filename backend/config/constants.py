"""
LaborGuard Config — Constants
All trigger thresholds, plan limits, and application constants
"""

# =============================================
# PARAMETRIC TRIGGER THRESHOLDS
# =============================================
TRIGGER_THRESHOLDS = {
    "HEAVY_RAIN": {
        "threshold": 80,        # mm/hr
        "unit": "mm/hr",
        "source": "OpenWeatherMap",
    },
    "FLOOD": {
        "threshold": "RED",     # IMD Red Alert
        "unit": "alert_level",
        "source": "IMD Alert API",
    },
    "HEAT": {
        "threshold": 43,        # °C sustained
        "unit": "°C",
        "source": "OpenWeatherMap",
    },
    "AQI": {
        "threshold": 400,       # AQI value (Hazardous)
        "unit": "AQI",
        "source": "AQICN API",
    },
    "ORDER_SUSPENSION": {
        "threshold": 2,         # hours of downtime
        "unit": "hours",
        "source": "Zomato Mock API",
    },
}

# =============================================
# TRIPLE-SOURCE CROSS-VALIDATION
# =============================================
VALIDATION_RULES = {
    3: "AUTO_APPROVE",      # All 3 sources agree → instant payout
    2: "SOFT_VERIFY",       # 2 agree → minor delay
    1: "HOLD_FOR_REVIEW",   # Only 1 → manual review
}

# =============================================
# PLAN TIERS
# =============================================
PLAN_TIERS = {
    "BASIC": {
        "name": "Basic Shield",
        "coverage_multiplier": 1.0,
        "premium_multiplier": 1.0,
        "description": "Essential income protection",
        "features": [
            "Heavy rainfall & flood coverage",
            "Payout within 2 hours",
            "Up to 1x weekly earnings",
        ],
    },
    "STANDARD": {
        "name": "Standard Shield",
        "coverage_multiplier": 1.5,
        "premium_multiplier": 1.4,
        "description": "Enhanced protection with faster payouts",
        "features": [
            "All Basic features",
            "Heat & AQI coverage",
            "Instant Green-tier payout",
            "Up to 1.5x weekly earnings",
        ],
    },
    "PREMIUM": {
        "name": "Premium Shield",
        "coverage_multiplier": 2.0,
        "premium_multiplier": 1.8,
        "description": "Maximum protection",
        "features": [
            "All Standard features",
            "Platform suspension coverage",
            "Instant Green & Amber payout",
            "Up to 2x weekly earnings",
            "₹50 false positive goodwill",
        ],
    },
}

# =============================================
# PREMIUM RANGE
# =============================================
MIN_PREMIUM = 29    # ₹29/week
MAX_PREMIUM = 75    # ₹75/week

# =============================================
# FRAUD DETECTION TIERS
# =============================================
FRAUD_TIERS = {
    "GREEN": {"min": 0, "max": 30, "action": "Auto-approve, instant UPI payout"},
    "AMBER": {"min": 31, "max": 60, "action": "Soft verify, one-tap confirm"},
    "RED": {"min": 61, "max": 100, "action": "Hold for review, manual in 2hrs"},
}

# =============================================
# TRUST SCORE
# =============================================
TRUST_SCORE_BASE = 50.0
TRUST_SCORE_MAX = 100.0
VERIFIED_PARTNER_THRESHOLD = 80.0
PROBATION_WEEKS = 2

# Strike policy
STRIKE_ACTIONS = {
    1: "Warning — no penalty",
    2: "Premium increases next week",
    3: "Account suspended + legal report",
}

# =============================================
# PAYOUT LIMITS
# =============================================
PAYOUT_CAP_MULTIPLIER = 2      # 2x weekly premium × plan multiplier
MANUAL_OVERRIDE_THRESHOLD = 1000  # ₹1000 — requires admin co-sign
GOODWILL_CREDIT = 50           # ₹50 for false positive reversals
APPEAL_WINDOW_HOURS = 48

# =============================================
# RING DETECTION
# =============================================
RING_SPATIAL_RADIUS_M = 100
RING_MIN_CLUSTER_SIZE = 5
RING_TIMING_WINDOW_SEC = 30
RING_REGISTRATION_SURGE_THRESHOLD = 10

# =============================================
# CITIES & DEFAULT ZONES
# =============================================
SUPPORTED_CITIES = [
    "Chennai", "Bengaluru", "Mumbai", "Hyderabad", "Delhi"
]

WORKING_HOURS_PER_DAY = 10
WORKING_DAYS_PER_WEEK = 6
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
