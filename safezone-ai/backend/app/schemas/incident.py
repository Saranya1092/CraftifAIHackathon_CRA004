"""Pydantic schemas for incidents."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IncidentResponse(BaseModel):
    id: str
    event_type: str
    zone_id: Optional[str]
    zone_name: Optional[str]
    severity: str
    status: str
    confidence: Optional[float]
    source: str
    detection_metadata: Optional[Dict[str, Any]]
    frame_timestamp: Optional[str]
    acknowledged_by: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentUpdate(BaseModel):
    status: Optional[str] = Field(default=None, pattern=r"^(active|acknowledged|resolved)$")
    acknowledged_by: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None, max_length=2000)


class IncidentListResponse(BaseModel):
    items: List[IncidentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class IncidentCreate(BaseModel):
    """Internal schema used by services."""
    event_type: str
    zone_id: Optional[str] = None
    zone_name: Optional[str] = None
    severity: str = "high"
    confidence: Optional[float] = None
    source: str = "simulated"
    detection_metadata: Optional[Dict[str, Any]] = None
    frame_timestamp: Optional[str] = None
