"""
Mock Zomato API
Simulates worker verification and order activity
"""

import random
import hashlib
from fastapi import APIRouter

router = APIRouter(prefix="/mock/zomato", tags=["Mock - Zomato"])


@router.get("/verify-worker")
async def verify_worker(worker_id: str = "ZW123456"):
    """Verify a Zomato worker ID."""
    # Simulate verification
    is_valid = not worker_id.startswith("INVALID")

    if is_valid:
        return {
            "verified": True,
            "worker_id": worker_id,
            "name": f"Worker {worker_id[-4:]}",
            "platform": "zomato",
            "status": "ACTIVE",
            "joined_date": "2024-06-15",
            "city": random.choice(["Chennai", "Bengaluru", "Mumbai", "Hyderabad", "Delhi"]),
            "rating": round(random.uniform(4.0, 5.0), 1),
            "total_deliveries": random.randint(500, 5000),
            "_source": "mock_zomato",
        }

    return {
        "verified": False,
        "worker_id": worker_id,
        "error": "Worker ID not found in Zomato database",
        "_source": "mock_zomato",
    }


@router.get("/order-activity")
async def get_order_activity(
    worker_id: str = "ZW123456",
    zone_code: str = "CHN-VEL-4B",
):
    """Get order activity for a worker in a zone."""
    is_suspended = random.random() < 0.05
    has_activity = not is_suspended and random.random() > 0.1

    orders = []
    if has_activity:
        count = random.randint(3, 12)
        for i in range(count):
            orders.append({
                "order_id": f"ORD{random.randint(100000, 999999)}",
                "status": random.choice(["DELIVERED", "DELIVERED", "DELIVERED", "IN_TRANSIT", "PICKED_UP"]),
                "restaurant": random.choice([
                    "Saravana Bhavan", "A2B", "Dindigul Thalappakatti",
                    "Paradise Biryani", "Barbeque Nation", "Dominos",
                ]),
                "amount": round(random.uniform(150, 600), 0),
                "delivery_fee": round(random.uniform(25, 60), 0),
                "time_minutes": random.randint(15, 45),
            })

    return {
        "worker_id": worker_id,
        "zone_code": zone_code,
        "orders_active": not is_suspended,
        "order_count_today": len(orders),
        "orders": orders,
        "zone_status": "SUSPENDED" if is_suspended else "ACTIVE",
        "suspension_reason": "Heavy rainfall - deliveries paused" if is_suspended else None,
        "suspension_hours": round(random.uniform(2.5, 5), 1) if is_suspended else 0,
        "_source": "mock_zomato",
    }


@router.get("/zone-status")
async def get_zone_status(zone_code: str = "CHN-VEL-4B"):
    """Get overall zone order status."""
    is_down = random.random() < 0.08

    return {
        "zone_code": zone_code,
        "status": "SUSPENDED" if is_down else "ACTIVE",
        "active_riders": 0 if is_down else random.randint(20, 80),
        "pending_orders": 0 if is_down else random.randint(5, 40),
        "avg_delivery_time_min": None if is_down else random.randint(20, 45),
        "downtime_hours": round(random.uniform(2, 6), 1) if is_down else 0,
        "reason": "Weather disruption" if is_down else None,
        "_source": "mock_zomato",
    }
