"""Pydantic schemas for analytics endpoints."""
from __future__ import annotations

from typing import List
from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_people_detected: int
    total_incidents: int
    active_incidents: int
    acknowledged_incidents: int
    resolved_incidents: int
    active_zones: int
    monitoring_status: str


class TrendPoint(BaseModel):
    timestamp: str
    incidents: int


class TrendsResponse(BaseModel):
    period: str  # "24h" | "7d" | "30d"
    data: List[TrendPoint]
