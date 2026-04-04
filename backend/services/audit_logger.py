"""
LaborGuard Audit Logger Service
Immutable SHA-256 audit trail for every claim state change
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import AuditLog


class AuditLogger:
    """Immutable audit log with SHA-256 hash chain."""

    @staticmethod
    def _compute_hash(
        entity_type: str,
        entity_id: str,
        action: str,
        actor_id: str,
        timestamp: str,
        previous_hash: str = "",
        data: dict = None,
    ) -> str:
        """Compute SHA-256 hash for audit entry, chained to previous entry."""
        payload = json.dumps({
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "actor_id": actor_id,
            "timestamp": timestamp,
            "previous_hash": previous_hash,
            "data": data or {},
        }, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    async def log(
        db: AsyncSession,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_id: str = None,
        actor_role: str = None,
        previous_state: dict = None,
        new_state: dict = None,
        ip_address: str = None,
        device_fingerprint: str = None,
        metadata: dict = None,
    ) -> AuditLog:
        """Create an immutable audit log entry."""
        # Get previous hash for chain
        result = await db.execute(
            select(AuditLog)
            .order_by(desc(AuditLog.created_at))
            .limit(1)
        )
        prev_entry = result.scalar_one_or_none()
        previous_hash = prev_entry.entry_hash if prev_entry else "GENESIS"

        now = datetime.now(timezone.utc)
        entry_hash = AuditLogger._compute_hash(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_id=actor_id or "SYSTEM",
            timestamp=now.isoformat(),
            previous_hash=previous_hash,
            data=new_state,
        )

        audit_entry = AuditLog(
            id=str(uuid.uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            actor_role=actor_role,
            previous_state=previous_state,
            new_state=new_state,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
            entry_hash=entry_hash,
            previous_hash=previous_hash,
            metadata_=metadata,
            created_at=now,
        )

        db.add(audit_entry)
        await db.flush()
        return audit_entry

    @staticmethod
    async def verify_chain(db: AsyncSession, limit: int = 100) -> dict:
        """Verify audit log hash chain integrity."""
        result = await db.execute(
            select(AuditLog)
            .order_by(AuditLog.created_at)
            .limit(limit)
        )
        entries = result.scalars().all()

        if not entries:
            return {"valid": True, "entries_checked": 0}

        broken_links = []
        for i, entry in enumerate(entries):
            if i == 0:
                if entry.previous_hash != "GENESIS":
                    broken_links.append({
                        "entry_id": entry.id,
                        "expected_previous": "GENESIS",
                        "actual_previous": entry.previous_hash,
                    })
            else:
                if entry.previous_hash != entries[i - 1].entry_hash:
                    broken_links.append({
                        "entry_id": entry.id,
                        "expected_previous": entries[i - 1].entry_hash,
                        "actual_previous": entry.previous_hash,
                    })

        return {
            "valid": len(broken_links) == 0,
            "entries_checked": len(entries),
            "broken_links": broken_links,
        }
