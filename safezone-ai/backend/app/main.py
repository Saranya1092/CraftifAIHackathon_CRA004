"""SafeZone AI – FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import configure_logging
from app.database.base import init_db
from app.mqtt.mqtt_service import mqtt_service

from app.api import health, monitoring, zones, incidents, analytics, export, events

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("SafeZone AI starting up")
    await init_db()
    logger.info("Database initialised")
    mqtt_service.connect()
    yield
    logger.info("SafeZone AI shutting down")
    mqtt_service.disconnect()
    from app.services.monitoring_service import monitoring_service
    await monitoring_service.stop()


app = FastAPI(
    title="SafeZone AI",
    description=(
        "Real-Time Workplace Safety Sentinel – "
        "CraftifAI PipeGen Hackathon MVP"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(monitoring.router, prefix=API_PREFIX)
app.include_router(zones.router, prefix=API_PREFIX)
app.include_router(incidents.router, prefix=API_PREFIX)
app.include_router(analytics.router, prefix=API_PREFIX)
app.include_router(export.router, prefix=API_PREFIX)
app.include_router(events.router, prefix=API_PREFIX)
