"""Export endpoints."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.services.incident_service import export_csv

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/incidents.csv")
async def export_incidents_csv(
    status: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> Response:
    csv_content = await export_csv(db, status=status, date_from=date_from, date_to=date_to)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=incidents.csv"},
    )
