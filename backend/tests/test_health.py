"""Tests for PRISM health check endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from prism.main import app


from prism.config import settings

@pytest.fixture
async def client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Health endpoint should always return 200 with status info."""
    response = await client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert data["environment"] == settings.ENVIRONMENT
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_response_schema(client: AsyncClient):
    """Health response should match expected schema."""
    response = await client.get("/api/health")
    data = response.json()

    required_fields = {"status", "version", "environment", "timestamp"}
    assert required_fields.issubset(data.keys())
