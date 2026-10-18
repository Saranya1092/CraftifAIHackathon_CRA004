"""Tests for the health endpoint."""
import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(async_client):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "monitoring" in data
    assert "mqtt" in data


@pytest.mark.asyncio
async def test_health_monitoring_fields(async_client):
    response = await async_client.get("/api/health")
    monitoring = response.json()["monitoring"]
    assert "status" in monitoring
    assert "adapter" in monitoring
