"""
Monitoring orchestrator.

Manages the lifecycle of the perception adapter and coordinates
zone-entry detection, incident creation, and MQTT publishing.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# SSE subscriber callbacks
_sse_subscribers: List[Callable[[Dict[str, Any]], None]] = []


def add_sse_subscriber(cb: Callable[[Dict[str, Any]], None]) -> None:
    _sse_subscribers.append(cb)


def remove_sse_subscriber(cb: Callable[[Dict[str, Any]], None]) -> None:
    _sse_subscribers.discard(cb) if hasattr(_sse_subscribers, "discard") else None
    try:
        _sse_subscribers.remove(cb)
    except ValueError:
        pass


def broadcast_event(event: Dict[str, Any]) -> None:
    for cb in list(_sse_subscribers):
        try:
            cb(event)
        except Exception:
            pass


class MonitoringService:
    """Singleton that tracks monitoring state and coordinates workers."""

    def __init__(self) -> None:
        self._status: str = "stopped"  # stopped | running | error
        self._start_time: Optional[datetime] = None
        self._task: Optional[asyncio.Task] = None
        self._total_detections: int = 0
        self._error_message: Optional[str] = None

    @property
    def status(self) -> str:
        return self._status

    @property
    def start_time(self) -> Optional[datetime]:
        return self._start_time

    @property
    def total_detections(self) -> int:
        return self._total_detections

    @property
    def error_message(self) -> Optional[str]:
        return self._error_message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self._status,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "total_detections": self._total_detections,
            "error_message": self._error_message,
            "adapter": settings.perception_adapter,
        }

    async def start(self, db_factory: Any, mqtt_service: Any) -> None:
        if self._status == "running":
            return
        self._status = "running"
        self._start_time = datetime.now(timezone.utc)
        self._error_message = None
        logger.info("Monitoring started with adapter=%s", settings.perception_adapter)
        self._task = asyncio.create_task(
            self._run_loop(db_factory, mqtt_service),
            name="monitoring-loop",
        )

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._status = "stopped"
        logger.info("Monitoring stopped")

    async def _run_loop(self, db_factory: Any, mqtt_service: Any) -> None:
        from app.perception.adapter_factory import get_adapter
        from app.services.zone_service import list_zones
        from app.services.incident_service import create_incident
        from app.schemas.incident import IncidentCreate
        from app.services.geometry import point_in_polygon, coords_to_tuples

        adapter = get_adapter(settings.perception_adapter)
        cooldown: Dict[str, datetime] = {}  # zone_id -> last incident time

        try:
            async for detections in adapter.stream():
                async with db_factory() as db:
                    zones = await list_zones(db)
                    active_zones = [z for z in zones if z.is_active]

                for det in detections:
                    self._total_detections += 1
                    if det.get("class") not in ("person", "pedestrian", 0):
                        continue
                    cx = det.get("cx", 0.5)
                    cy = det.get("cy", 0.5)

                    for zone in active_zones:
                        poly = coords_to_tuples(zone.coordinates)
                        if point_in_polygon(cx, cy, poly):
                            now = datetime.now(timezone.utc)
                            last = cooldown.get(zone.id)
                            if last and (now - last).total_seconds() < settings.incident_cooldown_seconds:
                                continue
                            cooldown[zone.id] = now

                            inc_data = IncidentCreate(
                                event_type="zone_entry",
                                zone_id=zone.id,
                                zone_name=zone.name,
                                severity="high",
                                confidence=det.get("confidence"),
                                source=settings.perception_adapter,
                                detection_metadata=det,
                                frame_timestamp=det.get("frame_timestamp"),
                            )
                            async with db_factory() as db:
                                incident = await create_incident(db, inc_data)

                            broadcast_event({"type": "incident", "incident_id": incident.id})
                            logger.info("Incident created id=%s zone=%s", incident.id, zone.name)

                            if mqtt_service:
                                await mqtt_service.publish_incident(incident)

        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self._status = "error"
            self._error_message = str(exc)
            logger.error("Monitoring loop error: %s", exc, exc_info=True)


# Application-level singleton
monitoring_service = MonitoringService()
