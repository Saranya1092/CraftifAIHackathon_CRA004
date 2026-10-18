"""Analytics endpoints."""
from datetime import datetime, timezone, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.models.incident import Incident
from app.schemas.analytics import SummaryResponse, TrendsResponse, TrendPoint
from app.services.incident_service import get_summary
from app.services.monitoring_service import monitoring_service
from app.services.zone_service import list_zones

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=SummaryResponse)
async def summary(db: AsyncSession = Depends(get_db)) -> SummaryResponse:
    s = await get_summary(db)
    zones = await list_zones(db)
    active_zones = sum(1 for z in zones if z.is_active)
    return SummaryResponse(
        total_people_detected=monitoring_service.total_detections,
        total_incidents=s["total_incidents"],
        active_incidents=s["active_incidents"],
        acknowledged_incidents=s["acknowledged_incidents"],
        resolved_incidents=s["resolved_incidents"],
        active_zones=active_zones,
        monitoring_status=monitoring_service.status,
    )


@router.get("/trends", response_model=TrendsResponse)
async def trends(
    period: str = Query(default="24h", pattern=r"^(24h|7d|30d)$"),
    db: AsyncSession = Depends(get_db),
) -> TrendsResponse:
    now = datetime.now(timezone.utc)
    if period == "24h":
        since = now - timedelta(hours=24)
        bucket_hours = 1
        buckets = 24
    elif period == "7d":
        since = now - timedelta(days=7)
        bucket_hours = 24
        buckets = 7
    else:
        since = now - timedelta(days=30)
        bucket_hours = 24
        buckets = 30

    result = await db.execute(
        select(Incident.created_at).where(Incident.created_at >= since)
    )
    timestamps = [row[0] for row in result.all()]

    # Build bucket counts
    data: List[TrendPoint] = []
    for i in range(buckets):
        bucket_start = since + timedelta(hours=bucket_hours * i)
        bucket_end = bucket_start + timedelta(hours=bucket_hours)
        count = sum(1 for t in timestamps if bucket_start <= t < bucket_end)
        data.append(TrendPoint(timestamp=bucket_start.isoformat(), incidents=count))

    return TrendsResponse(period=period, data=data)
