"""
LaborGuard Demo — Fraud Ring Simulation
Simulates 50 fake GPS claims to trigger DBSCAN ring detection
Run: python demo/fraud_ring_simulation.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
import uuid
import time
import math
import hashlib
from datetime import datetime, timezone, timedelta


def generate_ring_claims(
    ring_center_lat: float = 12.9815,
    ring_center_lon: float = 80.2180,
    num_members: int = 8,
    num_claims: int = 50,
    radius_meters: float = 80,
):
    """
    Simulate a coordinated fraud ring of GPS-spoofed claims.
    All claims clustered within a tight radius with synchronized timing.
    """

    print("=" * 60)
    print("🚨 LaborGuard Fraud Ring Simulation")
    print("=" * 60)
    print(f"Ring Center: ({ring_center_lat}, {ring_center_lon})")
    print(f"Members: {num_members}")
    print(f"Claims: {num_claims}")
    print(f"Radius: {radius_meters}m")
    print()

    # Generate ring member profiles
    members = []
    base_ip = f"103.{random.randint(50, 200)}.{random.randint(1, 250)}"

    for i in range(num_members):
        # Fraudsters come from different home zones
        home_zones = ["CHN-ANN-2A", "BLR-KOR-1A", "MUM-AND-1A", "HYD-HIB-1A", "DEL-CON-1A"]
        member = {
            "worker_id": str(uuid.uuid4()),
            "name": f"Fake Worker {i+1}",
            "phone": f"+91{random.randint(7000000000, 9999999999)}",
            "home_zone": random.choice(home_zones),
            "device_fingerprint": hashlib.sha256(f"device_{i}".encode()).hexdigest(),
            "ip_address": f"{base_ip}.{random.randint(1, 20)}",  # Same subnet
            "registered": datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
        }
        members.append(member)
        print(f"  👤 Member {i+1}: {member['name']} (Home: {member['home_zone']})")

    print()

    # Generate claims — all within tight radius and time window
    claims = []
    base_time = datetime.now(timezone.utc)

    for j in range(num_claims):
        member = random.choice(members)

        # Random position within ring radius
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, radius_meters)
        lat_offset = (dist * math.cos(angle)) / 111000
        lon_offset = (dist * math.sin(angle)) / (111000 * math.cos(math.radians(ring_center_lat)))

        claim = {
            "id": str(uuid.uuid4()),
            "worker_id": member["worker_id"],
            "latitude": ring_center_lat + lat_offset,
            "longitude": ring_center_lon + lon_offset,
            "timestamp": (base_time + timedelta(seconds=random.uniform(0, 30))).timestamp(),
            "home_zone": member["home_zone"],
            "ip_address": member["ip_address"],
            "trigger_type": "HEAVY_RAIN",
            "max_velocity": random.uniform(130, 200),  # Impossible speed
            "altitude_variance": random.uniform(0, 0.5),  # Too steady
            "motion_level": random.uniform(0, 0.1),  # No movement
        }
        claims.append(claim)

    print(f"📊 Generated {len(claims)} fake claims")
    print()

    # Run DBSCAN detection
    from backend.ml.ring_model import RingModel
    model = RingModel(eps_meters=100, min_samples=5)
    results = model.fit_predict(claims)

    print("=" * 60)
    print("🔍 DBSCAN Ring Detection Results")
    print("=" * 60)
    print(f"  Rings Detected: {results['rings_detected']}")
    print(f"  Noise Points: {results['noise_points']}")
    print(f"  Total Claims Analyzed: {results['total_points']}")
    print()

    for ring in results.get("clusters", []):
        print(f"  🚨 RING #{ring['cluster_id'] + 1}")
        print(f"     Members: {ring['member_count']}")
        print(f"     Center: ({ring['center_latitude']}, {ring['center_longitude']})")
        print(f"     Radius: {ring['radius_meters']}m")
        print(f"     Confidence: {ring['confidence']}%")
        print(f"     Severity: {ring['severity']}")
        print(f"     Detection Methods: {', '.join(ring['detection_methods'])}")
        print(f"     Home Zones: {', '.join(ring['home_zones'])}")
        print(f"     Timing Spread: {ring['timing_spread_seconds']}s")
        print()

    # Fraud signals analysis
    print("=" * 60)
    print("📊 Individual Fraud Signal Analysis")
    print("=" * 60)

    from backend.ml.fraud_model import FraudModel
    fraud_model = FraudModel()

    flagged_count = 0
    for claim in claims[:5]:  # Show first 5
        result = fraud_model.compute_anomaly_score({
            "max_velocity": claim["max_velocity"],
            "days_in_zone": 0,  # Zone mismatch
            "altitude_variance": claim["altitude_variance"],
            "motion_level": claim["motion_level"],
            "order_count": 0,
        })
        if result["fraud_score"] > 60:
            flagged_count += 1
        print(f"  Claim {claim['id'][:8]}... → Fraud Score: {result['fraud_score']:.1f} | Signals: {result['flagged_signals']}/7")

    print(f"\n  ... and {len(claims) - 5} more claims analyzed")
    print(f"\n✅ Simulation complete. {flagged_count}/5 shown would be flagged as RED tier.")

    return results


if __name__ == "__main__":
    generate_ring_claims()
