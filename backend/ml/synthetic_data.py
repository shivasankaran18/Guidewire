"""
LaborGuard ML - Synthetic Data Generator
Generates realistic data for all ML models
"""

import uuid
import random
import hashlib
from datetime import datetime, timedelta, timezone

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

CITIES = {
    "Chennai": {
        "zones": ["CHN-VEL-4B", "CHN-VEL-4A", "CHN-ANN-2A", "CHN-ANN-2B", "CHN-TNR-1A", "CHN-ADY-3A", "CHN-MYL-5A", "CHN-SHN-6A"],
        "lat_range": (12.88, 13.10),
        "lon_range": (80.20, 80.28),
    },
    "Bengaluru": {
        "zones": ["BLR-KOR-1A", "BLR-IND-2A", "BLR-WHT-3A", "BLR-HSR-4A"],
        "lat_range": (12.90, 13.00),
        "lon_range": (77.55, 77.75),
    },
    "Mumbai": {
        "zones": ["MUM-AND-1A", "MUM-BAN-2A", "MUM-DAD-3A"],
        "lat_range": (19.00, 19.15),
        "lon_range": (72.82, 72.90),
    },
    "Hyderabad": {
        "zones": ["HYD-HIB-1A", "HYD-GAC-2A"],
        "lat_range": (17.43, 17.45),
        "lon_range": (78.34, 78.40),
    },
    "Delhi": {
        "zones": ["DEL-CON-1A", "DEL-SAK-2A"],
        "lat_range": (28.50, 28.65),
        "lon_range": (77.20, 77.25),
    },
}

FIRST_NAMES = [
    "Ravi", "Kumar", "Suresh", "Rajesh", "Arun", "Vijay", "Karthik", "Sanjay",
    "Deepak", "Manoj", "Rahul", "Amit", "Pradeep", "Ganesh", "Venkat",
    "Arjun", "Dinesh", "Prakash", "Ramesh", "Mohan", "Ashok", "Vikram",
    "Babu", "Senthil", "Murali", "Santosh", "Naveen", "Sunil", "Raju", "Kishore",
]

LAST_NAMES = [
    "Kumar", "Singh", "Sharma", "Patel", "Verma", "Gupta", "Yadav", "Reddy",
    "Nair", "Pillai", "Iyer", "Rao", "Das", "Mishra", "Joshi",
]


class SyntheticDataGenerator:
    """Generate realistic synthetic data for all LaborGuard ML models."""

    @staticmethod
    def generate_workers(count: int = 50) -> list[dict]:
        """Generate synthetic worker profiles."""
        workers = []
        used_phones = set()

        for i in range(count):
            city = random.choice(list(CITIES.keys()))
            city_data = CITIES[city]
            zone = random.choice(city_data["zones"])

            # Generate unique phone
            while True:
                phone = f"+91{random.randint(7000000000, 9999999999)}"
                if phone not in used_phones:
                    used_phones.add(phone)
                    break

            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)

            tenure_weeks = random.randint(1, 104)
            daily_earnings = random.uniform(500, 900)
            trust_score = random.uniform(30, 95)

            worker = {
                "id": str(uuid.uuid4()),
                "phone": phone,
                "name": f"{first_name} {last_name}",
                "platform": random.choice(["zomato", "swiggy"]),
                "platform_worker_id": f"ZW{random.randint(100000, 999999)}",
                "aadhaar_last4": str(random.randint(1000, 9999)),
                "aadhaar_hash": hashlib.sha256(f"aadhaar_{i}".encode()).hexdigest(),
                "upi_id_hash": hashlib.sha256(f"upi_{first_name.lower()}".encode()).hexdigest(),
                "upi_id_masked": f"{first_name.lower()}****@upi",
                "device_fingerprint": hashlib.sha256(f"device_{i}".encode()).hexdigest(),
                "device_model": random.choice([
                    "Redmi Note 12", "Samsung Galaxy M13", "Realme C55",
                    "POCO M5", "Vivo Y22", "OPPO A77", "Samsung Galaxy A14",
                ]),
                "primary_zone_code": zone,
                "city": city,
                "avg_daily_earnings": round(daily_earnings, 2),
                "avg_weekly_earnings": round(daily_earnings * 6, 2),
                "tenure_weeks": tenure_weeks,
                "trust_score": round(trust_score, 1),
                "is_verified_partner": trust_score >= 80,
                "fraud_strikes": 0 if trust_score > 60 else random.randint(0, 2),
                "account_status": "ACTIVE" if tenure_weeks >= 2 else "PROBATION",
                "role": "WORKER",
            }
            workers.append(worker)

        # Add admin and super admin
        workers.append({
            "id": str(uuid.uuid4()),
            "phone": "+919999900001",
            "name": "Admin Priya",
            "platform": "zomato",
            "platform_worker_id": "ADMIN001",
            "primary_zone_code": "CHN-ANN-2A",
            "city": "Chennai",
            "avg_daily_earnings": 0,
            "avg_weekly_earnings": 0,
            "tenure_weeks": 52,
            "trust_score": 100,
            "is_verified_partner": True,
            "fraud_strikes": 0,
            "account_status": "ACTIVE",
            "role": "ADMIN",
        })

        workers.append({
            "id": str(uuid.uuid4()),
            "phone": "+919999900000",
            "name": "Super Admin",
            "platform": "zomato",
            "platform_worker_id": "SADMIN001",
            "primary_zone_code": "CHN-ANN-2A",
            "city": "Chennai",
            "avg_daily_earnings": 0,
            "avg_weekly_earnings": 0,
            "tenure_weeks": 104,
            "trust_score": 100,
            "is_verified_partner": True,
            "fraud_strikes": 0,
            "account_status": "ACTIVE",
            "role": "SUPER_ADMIN",
        })

        return workers

    @staticmethod
    def generate_claims(workers: list[dict], count: int = 100) -> list[dict]:
        """Generate synthetic claims data."""
        claims = []
        trigger_types = ["HEAVY_RAIN", "FLOOD", "HEAT", "AQI", "ORDER_SUSPENSION"]

        for _ in range(count):
            worker = random.choice([w for w in workers if w.get("role") == "WORKER"])
            trigger_type = random.choice(trigger_types)
            is_genuine = random.random() > 0.15  # 85% genuine

            disruption_hours = random.uniform(2, 8)
            daily_earnings = worker.get("avg_daily_earnings", 700)
            calculated_payout = daily_earnings * (disruption_hours / 10) * random.uniform(1.0, 2.0)

            if is_genuine:
                fraud_score = random.uniform(0, 30)
                fraud_tier = "GREEN"
                status = random.choice(["APPROVED", "PAID", "PAID", "PAID"])
            else:
                fraud_score = random.uniform(40, 100)
                fraud_tier = "AMBER" if fraud_score < 60 else "RED"
                status = random.choice(["PENDING", "REJECTED", "APPROVED"])

            claims.append({
                "id": str(uuid.uuid4()),
                "worker_id": worker["id"],
                "worker_name": worker["name"],
                "zone_code": worker["primary_zone_code"],
                "city": worker.get("city", "Chennai"),
                "claim_type": trigger_type,
                "disruption_hours": round(disruption_hours, 1),
                "calculated_payout": round(calculated_payout, 2),
                "actual_payout": round(calculated_payout * 0.95, 2) if status in ("APPROVED", "PAID") else None,
                "fraud_score": round(fraud_score, 1),
                "fraud_tier": fraud_tier,
                "confidence_score": round(100 - fraud_score, 1),
                "status": status,
                "claimed_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))).isoformat(),
            })

        return claims

    @staticmethod
    def generate_trigger_events(count: int = 30) -> list[dict]:
        """Generate synthetic trigger events."""
        events = []
        for _ in range(count):
            city = random.choice(list(CITIES.keys()))
            zone = random.choice(CITIES[city]["zones"])
            trigger_type = random.choice(["HEAVY_RAIN", "FLOOD", "HEAT", "AQI", "ORDER_SUSPENSION"])

            values = {
                "HEAVY_RAIN": random.uniform(85, 180),
                "FLOOD": None,
                "HEAT": random.uniform(43, 50),
                "AQI": random.randint(410, 500),
                "ORDER_SUSPENSION": random.uniform(2.5, 6),
            }

            events.append({
                "id": str(uuid.uuid4()),
                "zone_code": zone,
                "city": city,
                "trigger_type": trigger_type,
                "severity": random.choice(["MODERATE", "HIGH", "CRITICAL"]),
                "threshold_value": values[trigger_type],
                "sources_agreeing": random.choice([2, 3, 3, 3]),
                "auto_approved": random.random() > 0.3,
                "triggered_at": (datetime.now(timezone.utc) - timedelta(hours=random.randint(0, 72))).isoformat(),
                "status": random.choice(["ACTIVE", "ACTIVE", "EXPIRED"]),
            })

        return events
