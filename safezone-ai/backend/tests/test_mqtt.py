"""Tests for MQTT service with mocked paho client."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.mqtt.mqtt_service import MQTTService
from app.models.incident import Incident


def _make_incident() -> Incident:
    inc = Incident(
        id="test-incident-id",
        event_type="zone_entry",
        zone_id="zone-1",
        zone_name="Test Zone",
        severity="high",
        status="active",
        source="simulated",
        confidence=0.92,
    )
    inc.detection_metadata = {"class": "person"}
    inc.created_at = datetime.now(timezone.utc)
    return inc


class TestMQTTService:
    def test_initial_state_not_connected(self):
        svc = MQTTService()
        assert svc.is_connected is False

    def test_connect_sets_up_client(self):
        with patch("app.mqtt.mqtt_service.mqtt.Client") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            svc = MQTTService()
            svc.connect()
            mock_client.connect_async.assert_called_once()
            mock_client.loop_start.assert_called_once()

    def test_connect_failure_sets_error(self):
        with patch("app.mqtt.mqtt_service.mqtt.Client") as MockClient:
            MockClient.side_effect = Exception("Connection refused")
            svc = MQTTService()
            svc.connect()  # should not raise
            assert svc._connect_error is not None

    def test_on_connect_rc_zero_sets_connected(self):
        svc = MQTTService()
        svc._on_connect(MagicMock(), None, None, 0)
        assert svc.is_connected is True
        assert svc._connect_error is None

    def test_on_connect_rc_nonzero_sets_not_connected(self):
        svc = MQTTService()
        svc._on_connect(MagicMock(), None, None, 5)
        assert svc.is_connected is False
        assert svc._connect_error is not None

    def test_on_disconnect_clears_connected(self):
        svc = MQTTService()
        svc._connected = True
        svc._on_disconnect(MagicMock(), None, 1)
        assert svc.is_connected is False

    @pytest.mark.asyncio
    async def test_publish_incident_when_connected(self):
        svc = MQTTService()
        svc._connected = True
        mock_client = MagicMock()
        svc._client = mock_client

        inc = _make_incident()
        await svc.publish_incident(inc)

        mock_client.publish.assert_called_once()
        topic, payload_str = mock_client.publish.call_args[0][:2]
        payload = json.loads(payload_str)
        assert payload["event_id"] == "test-incident-id"
        assert payload["event_type"] == "zone_entry"
        assert payload["zone_id"] == "zone-1"
        assert "confidence" in payload

    @pytest.mark.asyncio
    async def test_publish_does_not_raise_when_disconnected(self):
        svc = MQTTService()
        svc._connected = False
        inc = _make_incident()
        # Should not raise
        await svc.publish_incident(inc)

    @pytest.mark.asyncio
    async def test_publish_does_not_raise_on_publish_error(self):
        svc = MQTTService()
        svc._connected = True
        mock_client = MagicMock()
        mock_client.publish.side_effect = Exception("Publish failed")
        svc._client = mock_client

        inc = _make_incident()
        await svc.publish_incident(inc)  # must not raise

    def test_status_dict_structure(self):
        svc = MQTTService()
        status = svc.status
        assert "connected" in status
        assert "broker" in status
        assert "topic_incidents" in status
