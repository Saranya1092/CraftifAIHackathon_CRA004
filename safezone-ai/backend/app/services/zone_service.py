"""CRUD operations for hazard zones."""
from __future__ import annotations

import json
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.zone import Zone
from app.schemas.zone import ZoneCreate, ZoneUpdate


async def list_zones(db: AsyncSession) -> List[Zone]:
    result = await db.execute(select(Zone).order_by(Zone.created_at))
    return list(result.scalars().all())


async def get_zone(db: AsyncSession, zone_id: str) -> Optional[Zone]:
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    return result.scalar_one_or_none()


async def create_zone(db: AsyncSession, data: ZoneCreate) -> Zone:
    zone = Zone(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description or "",
        coordinates_json=json.dumps([c.model_dump() for c in data.coordinates]),
        color=data.color or "#ef4444",
        is_active=data.is_active if data.is_active is not None else True,
    )
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return zone


async def update_zone(db: AsyncSession, zone: Zone, data: ZoneUpdate) -> Zone:
    if data.name is not None:
        zone.name = data.name
    if data.description is not None:
        zone.description = data.description
    if data.coordinates is not None:
        zone.coordinates_json = json.dumps([c.model_dump() for c in data.coordinates])
    if data.color is not None:
        zone.color = data.color
    if data.is_active is not None:
        zone.is_active = data.is_active
    await db.commit()
    await db.refresh(zone)
    return zone


async def delete_zone(db: AsyncSession, zone: Zone) -> None:
    await db.delete(zone)
    await db.commit()
