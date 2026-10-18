"""
MQTT publishing service.

Publishes safety incidents to an MQTT broker using paho-mqtt.
Failures do NOT propagate to callers; incidents are already persisted
before this service is invoked.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Optional

import paho.mqtt.client as mqtt

from app.core.config import settings
from app.models.incident import Incident

logger = logging.getLogger(__name__)


class MQTTService:
    def __init__(self) -> None:
        self._client: Optional[mqtt.Client] = None
        self._connected: bool = False
        self._connect_error: Optional[str] = None

    def connect(self) -> None:
        """Establish connection to the MQTT broker (non-blocking)."""
        try:
            client = mqtt.Client(client_id=settings.mqtt_client_id)
            client.on_connect = self._on_connect
            client.on_disconnect = self._on_disconnect

            if settings.mqtt_username:
                client.username_pw_set(settings.mqtt_username, settings.mqtt_password)

            client.connect_async(settings.mqtt_broker_host, settings.mqtt_broker_port, keepalive=60)
            client.loop_start()
            self._client = client
            logger.info(
                "MQTT connecting to %s:%s", settings.mqtt_broker_host, settings.mqtt_broker_port
            )
        except Exception as exc:
            self._connect_error = str(exc)
            logger.error("MQTT connection failed: %s", exc)

    def disconnect(self) -> None:
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._client = None
        self._connected = False

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Any, rc: int) -> None:
        if rc == 0:
            self._connected = True
            self._connect_error = None
            logger.info("MQTT connected (rc=0)")
        else:
            self._connected = False
            self._connect_error = f"MQTT connect refused rc={rc}"
            logger.warning("MQTT connection refused rc=%s", rc)

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        self._connected = False
        if rc != 0:
            logger.warning("MQTT unexpected disconnect rc=%s – will auto-reconnect", rc)

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def status(self) -> dict:
        return {
            "connected": self._connected,
            "broker": f"{settings.mqtt_broker_host}:{settings.mqtt_broker_port}",
            "topic_incidents": settings.mqtt_topic_incidents,
            "error": self._connect_error,
        }

    async def publish_incident(self, incident: Incident) -> None:
        """Publish incident JSON.  Failures are logged, never raised."""
        if not self._client or not self._connected:
            logger.warning(
                "MQTT not connected – incident %s not published", incident.id
            )
            return
        payload = {
            "event_id": incident.id,
            "timestamp": incident.created_at.isoformat(),
            "event_type": incident.event_type,
            "zone_id": incident.zone_id,
            "severity": incident.severity,
            "source": incident.source,
            "confidence": incident.confidence,
            "detection_metadata": incident.detection_metadata,
        }
        topic = settings.mqtt_topic_incidents
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._client.publish(topic, json.dumps(payload), qos=1),
            )
            logger.info("MQTT published incident %s to %s", incident.id, topic)
        except Exception as exc:
            logger.error("MQTT publish error for incident %s: %s", incident.id, exc)


# Application-level singleton
mqtt_service = MQTTService()
