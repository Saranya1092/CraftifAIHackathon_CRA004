"""Tests for incident cooldown and deduplication logic."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncGenerator, Dict, List

import pytest

from app.services.geometry import point_in_polygon, coords_to_tuples


class TestCooldown:
    """Unit test the cooldown map logic extracted from monitoring_service."""

    def _should_create_incident(
        self,
        zone_id: str,
        cooldown: Dict[str, datetime],
        cooldown_seconds: int = 5,
    ) -> bool:
        now = datetime.now(timezone.utc)
        last = cooldown.get(zone_id)
        if last and (now - last).total_seconds() < cooldown_seconds:
            return False
        cooldown[zone_id] = now
        return True

    def test_first_event_creates_incident(self):
        cooldown: Dict[str, datetime] = {}
        assert self._should_create_incident("zone-1", cooldown) is True

    def test_second_event_within_cooldown_skipped(self):
        cooldown: Dict[str, datetime] = {}
        self._should_create_incident("zone-1", cooldown)
        # Immediately call again – within cooldown
        assert self._should_create_incident("zone-1", cooldown) is False

    def test_event_after_cooldown_creates_incident(self):
        cooldown: Dict[str, datetime] = {}
        # Manually set the last event to 10 seconds ago
        cooldown["zone-1"] = datetime.now(timezone.utc) - timedelta(seconds=10)
        assert self._should_create_incident("zone-1", cooldown, cooldown_seconds=5) is True

    def test_different_zones_independent(self):
        cooldown: Dict[str, datetime] = {}
        assert self._should_create_incident("zone-1", cooldown) is True
        assert self._should_create_incident("zone-2", cooldown) is True

    def test_same_zone_independent_from_other(self):
        cooldown: Dict[str, datetime] = {}
        self._should_create_incident("zone-1", cooldown)
        # zone-2 should still create
        assert self._should_create_incident("zone-2", cooldown) is True
