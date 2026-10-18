"""Tests for zone CRUD endpoints and validation."""
import pytest

VALID_ZONE = {
    "name": "Machine Area",
    "description": "Around the press machine",
    "coordinates": [
        {"x": 0.1, "y": 0.1},
        {"x": 0.5, "y": 0.1},
        {"x": 0.5, "y": 0.5},
        {"x": 0.1, "y": 0.5},
    ],
    "color": "#ef4444",
    "is_active": True,
}


@pytest.mark.asyncio
async def test_create_zone(async_client):
    response = await async_client.post("/api/zones", json=VALID_ZONE)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Machine Area"
    assert len(data["coordinates"]) == 4
    assert "id" in data


@pytest.mark.asyncio
async def test_list_zones_empty(async_client):
    response = await async_client.get("/api/zones")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_zones_after_create(async_client):
    await async_client.post("/api/zones", json=VALID_ZONE)
    response = await async_client.get("/api/zones")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_update_zone(async_client):
    create_resp = await async_client.post("/api/zones", json=VALID_ZONE)
    zone_id = create_resp.json()["id"]
    response = await async_client.put(f"/api/zones/{zone_id}", json={"name": "Updated Zone"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Zone"


@pytest.mark.asyncio
async def test_delete_zone(async_client):
    create_resp = await async_client.post("/api/zones", json=VALID_ZONE)
    zone_id = create_resp.json()["id"]
    del_resp = await async_client.delete(f"/api/zones/{zone_id}")
    assert del_resp.status_code == 204
    list_resp = await async_client.get("/api/zones")
    assert list_resp.json() == []


@pytest.mark.asyncio
async def test_get_nonexistent_zone_returns_404(async_client):
    response = await async_client.put("/api/zones/nonexistent", json={"name": "x"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_zone_with_too_few_vertices_rejected(async_client):
    bad_zone = {**VALID_ZONE, "coordinates": [{"x": 0.1, "y": 0.1}, {"x": 0.5, "y": 0.5}]}
    response = await async_client.post("/api/zones", json=bad_zone)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_zone_with_invalid_coordinates_rejected(async_client):
    # x > 1.0 is invalid
    bad_zone = {
        **VALID_ZONE,
        "coordinates": [
            {"x": 1.5, "y": 0.1},
            {"x": 0.5, "y": 0.1},
            {"x": 0.5, "y": 0.5},
        ],
    }
    response = await async_client.post("/api/zones", json=bad_zone)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_zone_invalid_color_rejected(async_client):
    bad_zone = {**VALID_ZONE, "color": "not-a-color"}
    response = await async_client.post("/api/zones", json=bad_zone)
    assert response.status_code == 422
