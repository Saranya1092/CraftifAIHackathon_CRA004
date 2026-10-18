"""Tests for incident management, filtering, pagination, and CSV export."""
import pytest


async def _create_zone(client, name="Test Zone"):
    resp = await client.post("/api/zones", json={
        "name": name,
        "coordinates": [
            {"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 0.0},
            {"x": 1.0, "y": 1.0}, {"x": 0.0, "y": 1.0},
        ],
        "is_active": True,
    })
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_incidents_empty(async_client):
    response = await async_client.get("/api/incidents")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_get_nonexistent_incident(async_client):
    response = await async_client.get("/api/incidents/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_incident_status(async_client, db_session):
    from app.services.incident_service import create_incident
    from app.schemas.incident import IncidentCreate

    inc = await create_incident(db_session, IncidentCreate(
        event_type="zone_entry",
        zone_id="zone-1",
        zone_name="Zone A",
        severity="high",
        source="simulated",
    ))

    response = await async_client.patch(f"/api/incidents/{inc.id}", json={
        "status": "acknowledged",
        "acknowledged_by": "operator@example.com",
        "notes": "Investigated – no hazard",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "acknowledged"
    assert data["acknowledged_by"] == "operator@example.com"


@pytest.mark.asyncio
async def test_patch_invalid_status_rejected(async_client, db_session):
    from app.services.incident_service import create_incident
    from app.schemas.incident import IncidentCreate

    inc = await create_incident(db_session, IncidentCreate(
        event_type="zone_entry", source="simulated"
    ))
    response = await async_client.patch(f"/api/incidents/{inc.id}", json={"status": "deleted"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_incident_persistence(async_client, db_session):
    from app.services.incident_service import create_incident, get_incident
    from app.schemas.incident import IncidentCreate

    inc = await create_incident(db_session, IncidentCreate(
        event_type="zone_entry", source="simulated", zone_id="z1", zone_name="Z1"
    ))
    fetched = await get_incident(db_session, inc.id)
    assert fetched is not None
    assert fetched.id == inc.id
    assert fetched.zone_name == "Z1"


@pytest.mark.asyncio
async def test_incident_pagination(async_client, db_session):
    from app.services.incident_service import create_incident
    from app.schemas.incident import IncidentCreate

    for i in range(5):
        await create_incident(db_session, IncidentCreate(
            event_type="zone_entry", source="simulated"
        ))

    resp1 = await async_client.get("/api/incidents?page=1&page_size=3")
    assert resp1.status_code == 200
    d1 = resp1.json()
    assert d1["total"] == 5
    assert len(d1["items"]) == 3
    assert d1["total_pages"] == 2

    resp2 = await async_client.get("/api/incidents?page=2&page_size=3")
    assert len(resp2.json()["items"]) == 2


@pytest.mark.asyncio
async def test_incident_filter_by_status(async_client, db_session):
    from app.services.incident_service import create_incident, update_incident
    from app.schemas.incident import IncidentCreate, IncidentUpdate

    inc1 = await create_incident(db_session, IncidentCreate(event_type="zone_entry", source="simulated"))
    inc2 = await create_incident(db_session, IncidentCreate(event_type="zone_entry", source="simulated"))
    await update_incident(db_session, inc2, IncidentUpdate(status="resolved"))

    resp = await async_client.get("/api/incidents?status=resolved")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == inc2.id


@pytest.mark.asyncio
async def test_csv_export(async_client, db_session):
    from app.services.incident_service import create_incident
    from app.schemas.incident import IncidentCreate

    await create_incident(db_session, IncidentCreate(event_type="zone_entry", source="simulated"))

    response = await async_client.get("/api/export/incidents.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    text = response.text
    assert "event_type" in text
    assert "zone_entry" in text


@pytest.mark.asyncio
async def test_analytics_summary(async_client):
    response = await async_client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_incidents" in data
    assert "monitoring_status" in data
    assert "active_zones" in data
