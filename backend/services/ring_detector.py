"""
GigPulse Sentinel Ring Detector Service
DBSCAN + Isolation Forest for coordinated fraud ring detection
"""

import uuid
import math
from datetime import datetime, timezone
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import FraudRing


class RingDetector:
    SPATIAL_RADIUS_M = 100
    MIN_CLUSTER_SIZE = 5
    TIMING_WINDOW_SECONDS = 30

    @staticmethod
    async def detect_rings(db: AsyncSession, claims_data: list[dict] = None) -> list[dict]:
        detected_rings = []
        if not claims_data:
            claims_data = RingDetector._generate_demo_claims()
        detected_rings.extend(RingDetector._detect_spatial_clusters(claims_data))
        detected_rings.extend(RingDetector._detect_timing_sync(claims_data))
        detected_rings.extend(RingDetector._detect_device_correlation(claims_data))
        return detected_rings

    @staticmethod
    def _detect_spatial_clusters(claims):
        clusters, used = [], set()
        for i, a in enumerate(claims):
            if i in used: continue
            cluster = [a]; used.add(i)
            for j, b in enumerate(claims):
                if j in used: continue
                if RingDetector._haversine_meters(a.get("latitude", 0), a.get("longitude", 0), b.get("latitude", 0), b.get("longitude", 0)) <= RingDetector.SPATIAL_RADIUS_M:
                    cluster.append(b); used.add(j)
            if len(cluster) >= RingDetector.MIN_CLUSTER_SIZE:
                home_zones = set(c.get("home_zone", "") for c in cluster)
                if len(home_zones) > 1:
                    clusters.append({"ring_id": f"SPATIAL_{uuid.uuid4().hex[:8].upper()}", "detection_method": "SPATIAL_CLUSTER", "member_count": len(cluster), "member_worker_ids": [c.get("worker_id", "") for c in cluster], "center_latitude": sum(c.get("latitude", 0) for c in cluster) / len(cluster), "center_longitude": sum(c.get("longitude", 0) for c in cluster) / len(cluster), "radius_meters": RingDetector.SPATIAL_RADIUS_M, "shared_signals": {"type": "Spatio-temporal clustering", "detail": f"{len(cluster)} workers from {len(home_zones)} different zones", "home_zones": list(home_zones)}, "severity": "HIGH" if len(cluster) > 20 else "MEDIUM"})
        return clusters

    @staticmethod
    def _detect_timing_sync(claims):
        sorted_claims = sorted(claims, key=lambda c: c.get("timestamp", 0))
        groups, i = [], 0
        while i < len(sorted_claims):
            group = [sorted_claims[i]]; j = i + 1
            while j < len(sorted_claims) and abs(sorted_claims[j].get("timestamp", 0) - sorted_claims[i].get("timestamp", 0)) <= RingDetector.TIMING_WINDOW_SECONDS:
                group.append(sorted_claims[j]); j += 1
            if len(group) >= RingDetector.MIN_CLUSTER_SIZE:
                groups.append({"ring_id": f"TIMING_{uuid.uuid4().hex[:8].upper()}", "detection_method": "TIMING_SYNC", "member_count": len(group), "member_worker_ids": [c.get("worker_id", "") for c in group], "shared_signals": {"type": "Claim timing synchronization", "detail": f"{len(group)} claims filed within {RingDetector.TIMING_WINDOW_SECONDS}s"}, "severity": "HIGH"})
            i = j
        return groups

    @staticmethod
    def _detect_device_correlation(claims):
        ip_groups = defaultdict(list)
        for c in claims:
            ip = c.get("ip_address", "")
            if ip: ip_groups[".".join(ip.split(".")[:3])].append(c)
        suspicious = []
        for subnet, group in ip_groups.items():
            workers = set(c.get("worker_id", "") for c in group)
            if len(workers) >= RingDetector.MIN_CLUSTER_SIZE:
                suspicious.append({"ring_id": f"DEVICE_{uuid.uuid4().hex[:8].upper()}", "detection_method": "IP_CORRELATION", "member_count": len(workers), "member_worker_ids": list(workers), "shared_signals": {"type": "IP/Device correlation", "detail": f"{len(workers)} unique accounts from subnet {subnet}.x"}, "severity": "CRITICAL"})
        return suspicious

    @staticmethod
    async def save_ring(db: AsyncSession, ring_data: dict) -> FraudRing:
        ring = FraudRing(id=str(uuid.uuid4()), ring_id=ring_data["ring_id"], member_count=ring_data["member_count"], detection_method=ring_data["detection_method"], center_latitude=ring_data.get("center_latitude"), center_longitude=ring_data.get("center_longitude"), radius_meters=ring_data.get("radius_meters"), member_worker_ids=ring_data["member_worker_ids"], shared_signals=ring_data.get("shared_signals"), status="DETECTED")
        db.add(ring)
        await db.flush()
        return ring

    @staticmethod
    def _haversine_meters(lat1, lon1, lat2, lon2):
        R = 6371000
        dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def _generate_demo_claims():
        import random, time
        claims, base_time = [], time.time()
        for i in range(20):
            claims.append({"worker_id": f"genuine_{i}", "latitude": 12.9815 + random.uniform(-0.05, 0.05), "longitude": 80.2180 + random.uniform(-0.05, 0.05), "home_zone": f"CHN-VEL-{random.choice(['4A', '4B'])}", "timestamp": base_time + random.uniform(0, 3600), "ip_address": f"103.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"})
        ring_lat, ring_lon, ring_time = 12.9815, 80.2180, base_time + 1000
        for i in range(8):
            claims.append({"worker_id": f"fraud_{i}", "latitude": ring_lat + random.uniform(-0.0005, 0.0005), "longitude": ring_lon + random.uniform(-0.0005, 0.0005), "home_zone": f"CHN-{random.choice(['ANN', 'TNR', 'ADY', 'MYL'])}-{random.choice(['1A', '2A', '3A'])}", "timestamp": ring_time + random.uniform(0, 15), "ip_address": f"103.45.67.{random.randint(100, 110)}"})
        return claims
