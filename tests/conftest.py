"""
Pytest configuration and fixtures for GigPulse Sentinel backend tests.
"""

import os
import sys
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_gigpulse.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("USE_MOCK_APIS", "true")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")

sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Initialize test database with schema."""
    from backend.models.database import init_db, close_db
    
    await init_db()
    yield
    await close_db()
    
    if os.path.exists("./test_gigpulse.db"):
        os.remove("./test_gigpulse.db")


@pytest.fixture
async def client():
    """Create FastAPI test client."""
    from backend.main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def worker_token(client):
    """Get demo worker JWT token."""
    response = await client.post("/api/auth/demo-login")
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def admin_token(client):
    """Get demo admin JWT token."""
    response = await client.post("/api/auth/demo-admin-login")
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def worker_headers(worker_token):
    """Headers for authenticated worker requests."""
    return {"Authorization": f"Bearer {worker_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """Headers for authenticated admin requests."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(autouse=True)
def mock_cerebras():
    """Mock Cerebras LLM calls to avoid API key requirement."""
    from unittest.mock import MagicMock
    
    mock_response = MagicMock()
    mock_response.answer = "This is a mocked response for testing."
    mock_response.category = "GENERAL"
    mock_response.related_claim_id = ""
    mock_response.suggested_actions = ["Check your claims history"]
    mock_response.sentiment = "NEUTRAL"
    
    def mock_invoke(pydantic_model, system_prompt, user_prompt):
        return mock_response
    
    with patch("backend.agents.base.invoke_with_structure", side_effect=mock_invoke):
        with patch("backend.agents.base.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.with_structured_output.return_value = mock_response
            mock_get_llm.return_value = mock_llm
            yield