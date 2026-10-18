"""CRUD and business logic for incidents."""
from __future__ import annotations

import csv
import io
import uuid
from datetime import datetime, timezone
from math import ceil
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate


async def create_incident(db: AsyncSession, data: IncidentCreate) -> Incident:
    from datetime import datetime, timezone
    incident = Incident(
        id=str(uuid.uuid4()),
        event_type=data.event_type,
        zone_id=data.zone_id,
        zone_name=data.zone_name,
        severity=data.severity,
        status="active",
        confidence=data.confidence,
        source=data.source,
        frame_timestamp=data.frame_timestamp,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    incident.detection_metadata = data.detection_metadata
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident


async def get_incident(db: AsyncSession, incident_id: str) -> Optional[Incident]:
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    return result.scalar_one_or_none()


async def list_incidents(
    db: AsyncSession,
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    zone_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Incident], int]:
    query = select(Incident)
    if status:
        query = query.where(Incident.status == status)
    if event_type:
        query = query.where(Incident.event_type == event_type)
    if zone_id:
        query = query.where(Incident.zone_id == zone_id)
    if date_from:
        query = query.where(Incident.created_at >= date_from)
    if date_to:
        query = query.where(Incident.created_at <= date_to)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = query.order_by(Incident.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def update_incident(db: AsyncSession, incident: Incident, data: IncidentUpdate) -> Incident:
    if data.status is not None:
        incident.status = data.status
    if data.acknowledged_by is not None:
        incident.acknowledged_by = data.acknowledged_by
    if data.notes is not None:
        incident.notes = data.notes
    incident.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(incident)
    return incident


async def get_summary(db: AsyncSession) -> dict:
    total = (await db.execute(select(func.count()).select_from(Incident))).scalar_one()
    active = (await db.execute(
        select(func.count()).select_from(Incident).where(Incident.status == "active")
    )).scalar_one()
    ack = (await db.execute(
        select(func.count()).select_from(Incident).where(Incident.status == "acknowledged")
    )).scalar_one()
    resolved = (await db.execute(
        select(func.count()).select_from(Incident).where(Incident.status == "resolved")
    )).scalar_one()
    return {
        "total_incidents": total,
        "active_incidents": active,
        "acknowledged_incidents": ack,
        "resolved_incidents": resolved,
    }


async def export_csv(
    db: AsyncSession,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> str:
    incidents, _ = await list_incidents(
        db, status=status, date_from=date_from, date_to=date_to, page=1, page_size=10000
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "event_type", "zone_id", "zone_name", "severity", "status",
        "confidence", "source", "frame_timestamp", "acknowledged_by", "notes",
        "created_at", "updated_at"
    ])
    for i in incidents:
        writer.writerow([
            i.id, i.event_type, i.zone_id or "", i.zone_name or "",
            i.severity, i.status, i.confidence or "", i.source,
            i.frame_timestamp or "", i.acknowledged_by or "", i.notes or "",
            i.created_at.isoformat(), i.updated_at.isoformat(),
        ])
    return output.getvalue()
