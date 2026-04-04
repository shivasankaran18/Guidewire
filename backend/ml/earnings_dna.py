"""
LaborGuard ML - Earnings DNA
Time-weighted earnings pattern analysis
"""

import random
from datetime import datetime, timezone


DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class EarningsDNA:
    """
    Earnings DNA profile builder.
    Captures time-weighted earnings patterns per worker.
    """

    @staticmethod
    def build_profile(worker_id: str, historical_data: list[dict] = None) -> dict:
        """
        Build a complete earnings DNA profile from historical order data.
        If no data provided, generates realistic synthetic patterns.
        """
        if not historical_data:
            historical_data = EarningsDNA._generate_synthetic_history(worker_id)

        # Build 7x24 heatmap (day × hour)
        heatmap = {}
        for day in range(7):
            for hour in range(24):
                key = f"{day}_{hour}"
                matching = [
                    d for d in historical_data
                    if d.get("day") == day and d.get("hour") == hour
                ]
                if matching:
                    avg_earnings = sum(d["earnings"] for d in matching) / len(matching)
                    avg_orders = sum(d["orders"] for d in matching) / len(matching)
                else:
                    avg_earnings = 0
                    avg_orders = 0

                heatmap[key] = {
                    "day": day,
                    "day_name": DAY_NAMES[day],
                    "hour": hour,
                    "avg_earnings": round(avg_earnings, 2),
                    "avg_orders": round(avg_orders, 1),
                    "sample_count": len(matching),
                }

        # Summary stats
        all_earnings = [v["avg_earnings"] for v in heatmap.values() if v["avg_earnings"] > 0]
        peak_slot = max(heatmap.values(), key=lambda x: x["avg_earnings"])

        daily_totals = {}
        for day in range(7):
            day_slots = [
                heatmap[f"{day}_{h}"]["avg_earnings"]
                for h in range(24)
            ]
            daily_totals[DAY_NAMES[day]] = round(sum(day_slots), 2)

        peak_day = max(daily_totals, key=daily_totals.get)
        avg_daily = round(sum(daily_totals.values()) / 7, 2)
        avg_weekly = round(sum(daily_totals.values()), 2)

        return {
            "worker_id": worker_id,
            "heatmap": list(heatmap.values()),
            "daily_totals": daily_totals,
            "peak_day": peak_day,
            "peak_hour": peak_slot["hour"],
            "peak_earnings": peak_slot["avg_earnings"],
            "avg_daily": avg_daily,
            "avg_weekly": avg_weekly,
            "active_hours": sum(1 for v in heatmap.values() if v["avg_earnings"] > 10),
            "profile_completeness": min(100, len(all_earnings) / 1.68 * 100),
        }

    @staticmethod
    def get_earnings_for_time(profile: dict, day: int, hour: int) -> float:
        """Get expected earnings for a specific day/hour from profile."""
        for slot in profile.get("heatmap", []):
            if slot["day"] == day and slot["hour"] == hour:
                return slot["avg_earnings"]
        return 0

    @staticmethod
    def _generate_synthetic_history(worker_id: str, weeks: int = 8) -> list[dict]:
        """Generate realistic synthetic earnings history."""
        data = []

        # Base earning patterns
        for week in range(weeks):
            for day in range(7):
                for hour in range(24):
                    # Night hours - very low activity
                    if hour < 6 or hour > 22:
                        if random.random() > 0.9:
                            earnings = random.uniform(5, 30)
                            orders = random.randint(0, 1)
                        else:
                            continue

                    # Morning slot
                    elif 6 <= hour <= 9:
                        earnings = random.uniform(30, 70)
                        orders = random.randint(1, 3)

                    # Lunch rush
                    elif 11 <= hour <= 14:
                        earnings = random.uniform(70, 140)
                        orders = random.randint(2, 6)

                    # Afternoon lull
                    elif 14 < hour < 17:
                        earnings = random.uniform(20, 50)
                        orders = random.randint(1, 2)

                    # Dinner rush
                    elif 17 <= hour <= 21:
                        earnings = random.uniform(90, 160)
                        orders = random.randint(3, 7)

                    else:
                        earnings = random.uniform(15, 40)
                        orders = random.randint(0, 2)

                    # Weekend boost
                    if day >= 5:
                        earnings *= random.uniform(1.2, 1.5)

                    # Friday evening peak
                    if day == 4 and 18 <= hour <= 21:
                        earnings *= random.uniform(1.3, 1.8)

                    # Random variation
                    earnings *= random.uniform(0.85, 1.15)

                    data.append({
                        "worker_id": worker_id,
                        "week": week,
                        "day": day,
                        "hour": hour,
                        "earnings": round(earnings, 2),
                        "orders": orders,
                    })

        return data


# Global instance
earnings_dna = EarningsDNA()
