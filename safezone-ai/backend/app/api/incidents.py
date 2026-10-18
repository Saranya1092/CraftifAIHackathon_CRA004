"""Incident management endpoints."""
from datetime import datetime
from math import ceil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.schemas.incident import IncidentListResponse, IncidentResponse, IncidentUpdate
from app.services import incident_service

router = APIRouter(prefix="/incidents", tags=["Incidents"])


def _to_response(i) -> IncidentResponse:
    return IncidentResponse(
        id=i.id,
        event_type=i.event_type,
        zone_id=i.zone_id,
        zone_name=i.zone_name,
        severity=i.severity,
        status=i.status,
        confidence=i.confidence,
        source=i.source,
        detection_metadata=i.detection_metadata,
        frame_timestamp=i.frame_timestamp,
        acknowledged_by=i.acknowledged_by,
        notes=i.notes,
        created_at=i.created_at,
        updated_at=i.updated_at,
    )


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    status: Optional[str] = Query(default=None),
    event_type: Optional[str] = Query(default=None),
    zone_id: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> IncidentListResponse:
    incidents, total = await incident_service.list_incidents(
        db,
        status=status,
        event_type=event_type,
        zone_id=zone_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return IncidentListResponse(
        items=[_to_response(i) for i in incidents],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, ceil(total / page_size)),
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)) -> IncidentResponse:
    incident = await incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _to_response(incident)


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def patch_incident(
    incident_id: str, data: IncidentUpdate, db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    incident = await incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident = await incident_service.update_incident(db, incident, data)
    return _to_response(incident)
