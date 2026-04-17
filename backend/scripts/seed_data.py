"""
GigPulse Sentinel - Database Seed Script
Populates the PostgreSQL database with realistic synthetic data using SQLAlchemy.
"""

import sys
import os
import asyncio
from datetime import datetime, timezone, timedelta
from backend.models.database import (
    engine, async_session, init_db, close_db,
    Worker, Claim, Policy, Trigger, Zone
)
from backend.ml.synthetic_data import SyntheticDataGenerator
import uuid


async def seed_database():
    print("🌱 Starting GigPulse Sentinel Database Seeding...")

    # Ensure tables exist (sqlite dev only). For Postgres, apply SQL migrations under `database/`.
    if engine.url.get_backend_name() == "sqlite":
        await init_db()

    async with async_session() as session:
        # Check if already seeded (by checking if any worker exists)
        from sqlalchemy import select
        result = await session.execute(select(Worker).limit(1))
        if result.scalar_one_or_none():
            print("⚠️ Database is already seeded. To re-seed, drop the tables first.")
            await close_db()
            return

        print("Generating synthetic data...")
        generator = SyntheticDataGenerator()
        workers_data = generator.generate_workers(50)
        
        # Load all zones to assign valid zone IDs
        zones_result = await session.execute(select(Zone))
        zones = {z.zone_code: z.id for z in zones_result.scalars().all()}
        
        print(f"Adding {len(workers_data)} workers...")
        db_workers = []
        for w_data in workers_data:
            w_data.pop("city", None)  # Remove extra field not in DB schema
            zone_code = w_data.get("primary_zone_code")
            if zone_code and zone_code in zones:
                w_data["zone_id"] = zones[zone_code]
                
            worker = Worker(**w_data)
            db_workers.append(worker)
            session.add(worker)
            
        await session.flush()
        
        print("Generating policies for active workers...")
        db_policies = []
        for worker in db_workers:
            if worker.account_status == "ACTIVE" and worker.role == "WORKER":
                policy = Policy(
                    id=str(uuid.uuid4()),
                    worker_id=worker.id,
                    plan_tier="STANDARD",
                    premium_amount=45.0,
                    coverage_amount=worker.avg_weekly_earnings * 1.5,
                    coverage_multiplier=1.5,
                    week_start=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    week_end=(datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d"),
                    status="ACTIVE",
                    payment_reference=f"UPI_{uuid.uuid4().hex[:12].upper()}",
                    payment_status="PAID"
                )
                db_policies.append(policy)
                session.add(policy)
                
        await session.flush()

        # Seed Claims
        print("Generating historical claims...")
        # Convert Worker objects back to dicts for the generator
        workers_dict = [{"id": w.id, "name": w.name, "primary_zone_code": w.primary_zone_code, "avg_daily_earnings": w.avg_daily_earnings, "role": w.role} for w in db_workers]
        claims_data = generator.generate_claims(workers_dict, 100)
        
        for i, c_data in enumerate(claims_data):
            c_data.pop("worker_name", None)
            c_data.pop("city", None)
            
            # Find a matching policy and trigger (mocking IDs for historical data)
            policy_id = db_policies[i % len(db_policies)].id if db_policies else str(uuid.uuid4())
            
            # Format datetime
            claimed_at = datetime.fromisoformat(c_data["claimed_at"].replace("Z", "+00:00"))
            c_data["claimed_at"] = claimed_at
            
            claim = Claim(
                id=c_data["id"],
                worker_id=c_data["worker_id"],
                policy_id=policy_id,               # Fake policy id mapping
                trigger_id=str(uuid.uuid4()),      # Fake trigger mapping
                zone_code=c_data["zone_code"],
                claim_type=c_data["claim_type"],
                disruption_hours=c_data["disruption_hours"],
                working_hours=10.0,
                calculated_payout=c_data["calculated_payout"],
                actual_payout=c_data.get("actual_payout"),
                fraud_score=c_data["fraud_score"],
                fraud_tier=c_data["fraud_tier"],
                confidence_score=c_data["confidence_score"],
                status=c_data["status"],
                claimed_at=claimed_at,
            )
            session.add(claim)

        await session.commit()
        print("✅ Database successfully seeded!")

    await close_db()


if __name__ == "__main__":
    # Add backend parent to python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    asyncio.run(seed_database())
