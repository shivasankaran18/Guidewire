"""
LaborGuard ML - Ring Detection Model
DBSCAN clustering for coordinated fraud ring detection
"""

import numpy as np
import math
from collections import defaultdict


class RingModel:
    """
    DBSCAN-based fraud ring detection model.
    Identifies clusters of coordinated fraudulent behavior.
    """

    def __init__(self, eps_meters: float = 100, min_samples: int = 5):
        self.eps = eps_meters  # 100m radius
        self.min_samples = min_samples  # Minimum 5 for a ring

    def fit_predict(self, claims_data: list[dict]) -> dict:
        """
        Run DBSCAN clustering on claims data.
        Returns cluster labels and ring analysis.
        """
        if not claims_data:
            return {"clusters": [], "noise_points": 0, "rings_detected": 0}

        n = len(claims_data)
        labels = [-1] * n  # -1 = noise
        cluster_id = 0
        visited = [False] * n

        for i in range(n):
            if visited[i]:
                continue
            visited[i] = True

            neighbors = self._region_query(claims_data, i)

            if len(neighbors) >= self.min_samples:
                # Expand cluster
                self._expand_cluster(
                    claims_data, labels, i, neighbors, cluster_id, visited
                )
                cluster_id += 1

        # Analyze clusters
        clusters = defaultdict(list)
        noise_count = 0
        for idx, label in enumerate(labels):
            if label == -1:
                noise_count += 1
            else:
                clusters[label].append(claims_data[idx])

        # Build ring analysis
        rings = []
        for cid, members in clusters.items():
            if len(members) >= self.min_samples:
                ring = self._analyze_ring(cid, members)
                rings.append(ring)

        return {
            "clusters": rings,
            "noise_points": noise_count,
            "rings_detected": len(rings),
            "total_points": n,
            "labels": labels,
        }

    def _region_query(self, data: list[dict], point_idx: int) -> list[int]:
        """Find all points within eps distance of point."""
        neighbors = []
        point = data[point_idx]
        for j, other in enumerate(data):
            dist = self._distance_meters(
                point.get("latitude", 0), point.get("longitude", 0),
                other.get("latitude", 0), other.get("longitude", 0),
            )
            if dist <= self.eps:
                neighbors.append(j)
        return neighbors

    def _expand_cluster(self, data, labels, point_idx, neighbors, cluster_id, visited):
        """Expand a DBSCAN cluster."""
        labels[point_idx] = cluster_id
        i = 0
        while i < len(neighbors):
            q = neighbors[i]
            if not visited[q]:
                visited[q] = True
                q_neighbors = self._region_query(data, q)
                if len(q_neighbors) >= self.min_samples:
                    neighbors.extend(q_neighbors)
            if labels[q] == -1:
                labels[q] = cluster_id
            i += 1

    def _analyze_ring(self, cluster_id: int, members: list[dict]) -> dict:
        """Analyze a detected ring cluster."""
        lats = [m.get("latitude", 0) for m in members]
        lons = [m.get("longitude", 0) for m in members]
        center_lat = np.mean(lats)
        center_lon = np.mean(lons)

        # Calculate radius
        max_dist = 0
        for m in members:
            d = self._distance_meters(
                center_lat, center_lon,
                m.get("latitude", 0), m.get("longitude", 0)
            )
            max_dist = max(max_dist, d)

        # Check home zone diversity
        home_zones = set(m.get("home_zone", "") for m in members)

        # Check timing synchronization
        timestamps = sorted(m.get("timestamp", 0) for m in members)
        timing_spread = timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0

        # Check IP correlation
        ips = set(m.get("ip_address", "") for m in members)
        ip_subnets = set(".".join(ip.split(".")[:3]) for ip in ips if ip)

        # Determine detection method
        detection_methods = []
        if len(home_zones) > 2:
            detection_methods.append("SPATIAL_CLUSTER")
        if timing_spread < 60:
            detection_methods.append("TIMING_SYNC")
        if len(ip_subnets) < len(members) / 3:
            detection_methods.append("IP_CORRELATION")

        # Confidence score
        confidence = min(100, len(detection_methods) * 30 + len(members) * 2)

        return {
            "cluster_id": cluster_id,
            "member_count": len(members),
            "center_latitude": round(center_lat, 7),
            "center_longitude": round(center_lon, 7),
            "radius_meters": round(max_dist, 1),
            "member_ids": [m.get("worker_id", "") for m in members],
            "home_zones": list(home_zones),
            "timing_spread_seconds": round(timing_spread, 1),
            "unique_ip_subnets": len(ip_subnets),
            "detection_methods": detection_methods,
            "confidence": confidence,
            "severity": "CRITICAL" if confidence > 70 else "HIGH" if confidence > 50 else "MEDIUM",
        }

    @staticmethod
    def _distance_meters(lat1, lon1, lat2, lon2) -> float:
        """Haversine distance in meters."""
        R = 6371000
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# Global model instance
ring_model = RingModel()
