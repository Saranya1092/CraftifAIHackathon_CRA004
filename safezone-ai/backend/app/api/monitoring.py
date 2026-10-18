"""Monitoring control endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.database.base import get_db, AsyncSessionLocal
from app.services.monitoring_service import monitoring_service
from app.mqtt.mqtt_service import mqtt_service

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


class MonitoringStatusResponse(BaseModel):
    status: str
    start_time: str | None
    total_detections: int
    error_message: str | None
    adapter: str


@router.get("/status", response_model=MonitoringStatusResponse)
async def get_status() -> MonitoringStatusResponse:
    d = monitoring_service.to_dict()
    return MonitoringStatusResponse(**d)


@router.post("/start")
async def start_monitoring() -> dict:
    await monitoring_service.start(AsyncSessionLocal, mqtt_service)
    return {"message": "Monitoring started", "status": monitoring_service.status}


@router.post("/stop")
async def stop_monitoring() -> dict:
    await monitoring_service.stop()
    return {"message": "Monitoring stopped", "status": monitoring_service.status}
