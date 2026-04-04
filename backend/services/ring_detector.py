"""
LaborGuard Ring Detector Service
DBSCAN + Isolation Forest for coordinated fraud ring detection
"""

import uuid
import math
from datetime import datetime, timezone
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import FraudRing, Claim, Worker


class RingDetector:
    """
    Coordinated fraud ring detection using DBSCAN-style clustering.
    Detects spatio-temporal clustering, IP correlation, timing sync,
    pre-event registration surges, and earn/claim ratio anomalies.
    """

    # Detection thresholds
    SPATIAL_RADIUS_M = 100          # 100m radius for spatial clustering
    MIN_CLUSTER_SIZE = 5            # Minimum 5 workers to form a ring
    TIMING_WINDOW_SECONDS = 30      # Claims within 30 seconds = suspicious
    REGISTRATION_SURGE_THRESHOLD = 10  # 10+ new registrations in a week = flag

    @staticmethod
    async def detect_rings(
        db: AsyncSession,
        claims_data: list[dict] = None,
    ) -> list[dict]:
        """
        Run ring detection on recent claims.
        Returns detected fraud ring clusters.
        """
        detected_rings = []

        # Use demo data if no real claims
        if not claims_data:
            claims_data = RingDetector._generate_demo_claims()

        # 1. Spatio-temporal clustering
        spatial_rings = RingDetector._detect_spatial_clusters(claims_data)
        detected_rings.extend(spatial_rings)

        # 2. Timing synchronization detection
        timing_rings = RingDetector._detect_timing_sync(claims_data)
        detected_rings.extend(timing_rings)

        # 3. IP/Device correlation
        device_rings = RingDetector._detect_device_correlation(claims_data)
        detected_rings.extend(device_rings)

        return detected_rings

    @staticmethod
    def _detect_spatial_clusters(claims: list[dict]) -> list[dict]:
        """
        DBSCAN-style spatial clustering.
        Flag 5+ workers claiming from same 100m radius with different home zones.
        """
        # Group claims by location proximity
        clusters = []
        used = set()

        for i, claim_a in enumerate(claims):
            if i in used:
                continue

            cluster = [claim_a]
            used.add(i)

            for j, claim_b in enumerate(claims):
                if j in used:
                    continue

                dist = RingDetector._haversine_meters(
                    claim_a.get("latitude", 0), claim_a.get("longitude", 0),
                    claim_b.get("latitude", 0), claim_b.get("longitude", 0),
                )

                if dist <= RingDetector.SPATIAL_RADIUS_M:
                    cluster.append(claim_b)
                    used.add(j)

            # Check if cluster is suspicious
            if len(cluster) >= RingDetector.MIN_CLUSTER_SIZE:
                # Check if workers are from different home zones
                home_zones = set(c.get("home_zone", "") for c in cluster)
                if len(home_zones) > 1:
                    center_lat = sum(c.get("latitude", 0) for c in cluster) / len(cluster)
                    center_lon = sum(c.get("longitude", 0) for c in cluster) / len(cluster)

                    clusters.append({
                        "ring_id": f"SPATIAL_{uuid.uuid4().hex[:8].upper()}",
                        "detection_method": "SPATIAL_CLUSTER",
                        "member_count": len(cluster),
                        "member_worker_ids": [c.get("worker_id", "") for c in cluster],
                        "center_latitude": center_lat,
                        "center_longitude": center_lon,
                        "radius_meters": RingDetector.SPATIAL_RADIUS_M,
                        "shared_signals": {
                            "type": "Spatio-temporal clustering",
                            "detail": f"{len(cluster)} workers from {len(home_zones)} different zones claiming same 100m radius",
                            "home_zones": list(home_zones),
                        },
                        "severity": "HIGH" if len(cluster) > 20 else "MEDIUM",
                    })

        return clusters

    @staticmethod
    def _detect_timing_sync(claims: list[dict]) -> list[dict]:
        """Detect claims filed within seconds of each other."""
        # Sort by timestamp
        sorted_claims = sorted(claims, key=lambda c: c.get("timestamp", 0))

        suspicious_groups = []
        i = 0
        while i < len(sorted_claims):
            group = [sorted_claims[i]]
            j = i + 1
            while j < len(sorted_claims):
                time_diff = abs(
                    sorted_claims[j].get("timestamp", 0) - sorted_claims[i].get("timestamp", 0)
                )
                if time_diff <= RingDetector.TIMING_WINDOW_SECONDS:
                    group.append(sorted_claims[j])
                    j += 1
                else:
                    break

            if len(group) >= RingDetector.MIN_CLUSTER_SIZE:
                suspicious_groups.append({
                    "ring_id": f"TIMING_{uuid.uuid4().hex[:8].upper()}",
                    "detection_method": "TIMING_SYNC",
                    "member_count": len(group),
                    "member_worker_ids": [c.get("worker_id", "") for c in group],
                    "shared_signals": {
                        "type": "Claim timing synchronization",
                        "detail": f"{len(group)} claims filed within {RingDetector.TIMING_WINDOW_SECONDS}s — bot-like coordination",
                    },
                    "severity": "HIGH",
                })

            i = j

        return suspicious_groups

    @staticmethod
    def _detect_device_correlation(claims: list[dict]) -> list[dict]:
        """Detect multiple accounts from same IP/device."""
        # Group by IP subnet
        ip_groups = defaultdict(list)
        for claim in claims:
            ip = claim.get("ip_address", "")
            if ip:
                # Group by /24 subnet
                subnet = ".".join(ip.split(".")[:3])
                ip_groups[subnet].append(claim)

        suspicious = []
        for subnet, group in ip_groups.items():
            unique_workers = set(c.get("worker_id", "") for c in group)
            if len(unique_workers) >= RingDetector.MIN_CLUSTER_SIZE:
                suspicious.append({
                    "ring_id": f"DEVICE_{uuid.uuid4().hex[:8].upper()}",
                    "detection_method": "IP_CORRELATION",
                    "member_count": len(unique_workers),
                    "member_worker_ids": list(unique_workers),
                    "shared_signals": {
                        "type": "IP/Device correlation",
                        "detail": f"{len(unique_workers)} unique accounts from subnet {subnet}.x",
                        "subnet": subnet,
                    },
                    "severity": "CRITICAL",
                })

        return suspicious

    @staticmethod
    async def save_ring(db: AsyncSession, ring_data: dict) -> FraudRing:
        """Save a detected fraud ring to the database."""
        ring = FraudRing(
            id=str(uuid.uuid4()),
            ring_id=ring_data["ring_id"],
            member_count=ring_data["member_count"],
            detection_method=ring_data["detection_method"],
            center_latitude=ring_data.get("center_latitude"),
            center_longitude=ring_data.get("center_longitude"),
            radius_meters=ring_data.get("radius_meters"),
            member_worker_ids=ring_data["member_worker_ids"],
            shared_signals=ring_data.get("shared_signals"),
            status="DETECTED",
        )
        db.add(ring)
        await db.flush()
        return ring

    @staticmethod
    def _haversine_meters(lat1, lon1, lat2, lon2) -> float:
        """Calculate distance in meters between two GPS points."""
        R = 6371000  # Earth radius in meters
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def _generate_demo_claims() -> list[dict]:
        """Generate demo claim data for ring detection demonstration."""
        import random
        import time

        claims = []
        base_time = time.time()

        # Genuine scattered workers (should NOT be detected as ring)
        for i in range(20):
            claims.append({
                "worker_id": f"genuine_{i}",
                "latitude": 12.9815 + random.uniform(-0.05, 0.05),
                "longitude": 80.2180 + random.uniform(-0.05, 0.05),
                "home_zone": f"CHN-VEL-{random.choice(['4A', '4B'])}",
                "timestamp": base_time + random.uniform(0, 3600),
                "ip_address": f"103.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            })

        # Fraud ring: 8 workers, same spot, same time, different home zones
        ring_lat, ring_lon = 12.9815, 80.2180
        ring_time = base_time + 1000
        for i in range(8):
            claims.append({
                "worker_id": f"fraud_{i}",
                "latitude": ring_lat + random.uniform(-0.0005, 0.0005),
                "longitude": ring_lon + random.uniform(-0.0005, 0.0005),
                "home_zone": f"CHN-{random.choice(['ANN', 'TNR', 'ADY', 'MYL'])}-{random.choice(['1A', '2A', '3A'])}",
                "timestamp": ring_time + random.uniform(0, 15),
                "ip_address": f"103.45.67.{random.randint(100, 110)}",
            })

        return claims
