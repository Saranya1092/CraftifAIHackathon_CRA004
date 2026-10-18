"""Hazard zone CRUD endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.schemas.zone import ZoneCreate, ZoneResponse, ZoneUpdate
from app.services import zone_service

router = APIRouter(prefix="/zones", tags=["Zones"])


@router.get("", response_model=List[ZoneResponse])
async def list_zones(db: AsyncSession = Depends(get_db)) -> List[ZoneResponse]:
    zones = await zone_service.list_zones(db)
    result = []
    for z in zones:
        result.append(ZoneResponse(
            id=z.id,
            name=z.name,
            description=z.description,
            coordinates=z.coordinates,
            color=z.color,
            is_active=z.is_active,
            created_at=z.created_at,
            updated_at=z.updated_at,
        ))
    return result


@router.post("", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(data: ZoneCreate, db: AsyncSession = Depends(get_db)) -> ZoneResponse:
    zone = await zone_service.create_zone(db, data)
    return ZoneResponse(
        id=zone.id, name=zone.name, description=zone.description,
        coordinates=zone.coordinates, color=zone.color, is_active=zone.is_active,
        created_at=zone.created_at, updated_at=zone.updated_at,
    )


@router.put("/{zone_id}", response_model=ZoneResponse)
async def update_zone(
    zone_id: str, data: ZoneUpdate, db: AsyncSession = Depends(get_db)
) -> ZoneResponse:
    zone = await zone_service.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    zone = await zone_service.update_zone(db, zone, data)
    return ZoneResponse(
        id=zone.id, name=zone.name, description=zone.description,
        coordinates=zone.coordinates, color=zone.color, is_active=zone.is_active,
        created_at=zone.created_at, updated_at=zone.updated_at,
    )


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zone(zone_id: str, db: AsyncSession = Depends(get_db)) -> None:
    zone = await zone_service.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    await zone_service.delete_zone(db, zone)
