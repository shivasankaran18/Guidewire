"""
Backend API tests for GigPulse Sentinel.
Covers auth, worker, admin, and agent endpoints.
"""

import pytest


class TestAuth:
    """Test authentication endpoints."""

    async def test_demo_login_worker(self, client):
        """Test worker demo login returns valid token."""
        response = await client.post("/api/auth/demo-login")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["role"] == "WORKER"
        assert "worker_id" in data

    async def test_demo_login_admin(self, client):
        """Test admin demo login returns valid token."""
        response = await client.post("/api/auth/demo-admin-login")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["role"] == "ADMIN"

    async def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestWorkerProfile:
    """Test worker profile and data endpoints."""

    async def test_get_profile(self, client, worker_headers):
        """Test getting worker profile."""
        response = await client.get("/api/workers/profile", headers=worker_headers)
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "phone" in data
        assert "primary_zone_code" in data

    async def test_get_trust_score(self, client, worker_headers):
        """Test getting trust score."""
        response = await client.get("/api/workers/trust-score", headers=worker_headers)
        assert response.status_code == 200
        data = response.json()
        assert "trust_score" in data
        assert "fraud_strikes" in data

    async def test_get_notifications(self, client, worker_headers):
        """Test notifications endpoint returns list."""
        response = await client.get("/api/workers/notifications", headers=worker_headers)
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data


class TestPolicies:
    """Test policy endpoints."""

    async def test_get_current_policy(self, client, worker_headers):
        """Test getting current policy."""
        response = await client.get("/api/policies/current", headers=worker_headers)
        assert response.status_code == 200
        data = response.json()
        assert "has_active_policy" in data

    async def test_get_plans(self, client, worker_headers):
        """Test getting available plans."""
        response = await client.get("/api/policies/plans", headers=worker_headers)
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert "recommended_plan" in data


class TestTriggers:
    """Test trigger endpoints."""

    async def test_get_trigger_status(self, client, worker_headers):
        """Test getting trigger status for worker's zone."""
        response = await client.get("/api/triggers/status", headers=worker_headers)
        assert response.status_code == 200
        data = response.json()
        assert "zone_code" in data
        assert "active_triggers" in data


class TestClaims:
    """Test claim endpoints."""

    async def test_get_claims(self, client, worker_headers):
        """Test getting worker's claims."""
        response = await client.get("/api/claims/", headers=worker_headers)
        assert response.status_code == 200
        data = response.json()
        assert "claims" in data
        assert "total" in data

    async def test_get_claim_detail_not_found(self, client, worker_headers):
        """Test getting non-existent claim returns 404."""
        response = await client.get("/api/claims/non-existent-id", headers=worker_headers)
        assert response.status_code == 404


class TestPayouts:
    """Test payout endpoints."""

    async def test_get_payouts(self, client, worker_headers):
        """Test getting worker's payouts."""
        response = await client.get("/api/payouts/", headers=worker_headers)
        assert response.status_code == 200
        data = response.json()
        assert "payouts" in data
        assert "total_received" in data


class TestAdminDashboard:
    """Test admin dashboard endpoints."""

    async def test_admin_dashboard(self, client, admin_headers):
        """Test admin dashboard returns overview data."""
        response = await client.get("/api/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_workers" in data
        assert "pending_review_count" in data

    async def test_admin_claims_review(self, client, admin_headers):
        """Test getting claims for review."""
        response = await client.get("/api/admin/claims/review", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "claims" in data

    async def test_get_audit_log(self, client, admin_headers):
        """Test getting audit log."""
        response = await client.get("/api/admin/audit-log", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data or "demo_entries" in data

    async def test_verify_audit_chain(self, client, admin_headers):
        """Test verifying audit log chain."""
        response = await client.get("/api/admin/audit-log/verify", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "entries_checked" in data


class TestWorkerAgents:
    """Test worker-accessible AI agent endpoints."""

    async def test_chat(self, client, worker_headers):
        """Test worker chat with AI assistant."""
        response = await client.post(
            "/api/agents/chat",
            headers=worker_headers,
            json={"message": "What is my coverage?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

    async def test_earnings_insight(self, client, worker_headers):
        """Test earnings insight for worker."""
        response = await client.get("/api/agents/earnings-insight/demo-worker", headers=worker_headers)
        assert response.status_code in [200, 404]

    async def test_price_risk(self, client, worker_headers):
        """Test price risk for worker."""
        response = await client.get("/api/agents/price-risk/demo-worker", headers=worker_headers)
        assert response.status_code in [200, 404]


class TestAdminAgents:
    """Test admin-only AI agent endpoints."""

    async def test_investigate_claim(self, client, admin_headers):
        """Test fraud investigation on a claim."""
        response = await client.post(
            "/api/agents/investigate/demo-claim-id",
            headers=admin_headers,
            json={}
        )
        assert response.status_code in [200, 404]

    async def test_validate_trigger(self, client, admin_headers):
        """Test trigger validation."""
        response = await client.post(
            "/api/agents/validate-trigger/demo-trigger-id",
            headers=admin_headers
        )
        assert response.status_code in [200, 404]

    async def test_investigate_ring(self, client, admin_headers):
        """Test fraud ring investigation."""
        response = await client.post(
            "/api/agents/investigate-ring",
            headers=admin_headers,
            json={}
        )
        assert response.status_code == 200

    async def test_handle_appeal(self, client, admin_headers):
        """Test appeal handling."""
        response = await client.post(
            "/api/agents/handle-appeal/demo-claim-id",
            headers=admin_headers,
            json={"appeal_reason": "I believe my claim was genuine"}
        )
        assert response.status_code in [200, 404]


class TestSecurity:
    """Test security and authorization."""

    async def test_unauthenticated_access_denied(self, client):
        """Test accessing protected endpoint without token."""
        response = await client.get("/api/workers/profile")
        assert response.status_code == 401

    async def test_worker_cannot_access_admin(self, client, worker_headers):
        """Test worker cannot access admin-only endpoint."""
        response = await client.get("/api/admin/dashboard", headers=worker_headers)
        assert response.status_code == 403

    async def test_invalid_token_rejected(self, client):
        """Test invalid JWT token is rejected."""
        response = await client.get(
            "/api/workers/profile",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
