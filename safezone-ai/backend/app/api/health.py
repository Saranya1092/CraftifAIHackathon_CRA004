"""Health check endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.monitoring_service import monitoring_service
from app.mqtt.mqtt_service import mqtt_service

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    monitoring: dict
    mqtt: dict


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version="1.0.0",
        monitoring=monitoring_service.to_dict(),
        mqtt=mqtt_service.status,
    )
