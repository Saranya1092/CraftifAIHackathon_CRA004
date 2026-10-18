"""Pydantic schemas for hazard zones."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Coordinate(BaseModel):
    x: float = Field(..., ge=0.0, le=1.0, description="Normalised x in [0,1]")
    y: float = Field(..., ge=0.0, le=1.0, description="Normalised y in [0,1]")


class ZoneCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="", max_length=500)
    coordinates: List[Coordinate] = Field(..., min_length=3)
    color: Optional[str] = Field(default="#ef4444", pattern=r"^#[0-9a-fA-F]{6}$")
    is_active: Optional[bool] = True

    @field_validator("coordinates")
    @classmethod
    def coordinates_must_be_polygon(cls, v: List[Coordinate]) -> List[Coordinate]:
        if len(v) < 3:
            raise ValueError("A zone must have at least 3 vertices")
        return v


class ZoneUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    coordinates: Optional[List[Coordinate]] = Field(default=None, min_length=3)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    is_active: Optional[bool] = None

    @field_validator("coordinates")
    @classmethod
    def coordinates_must_be_polygon(cls, v: Optional[List[Coordinate]]) -> Optional[List[Coordinate]]:
        if v is not None and len(v) < 3:
            raise ValueError("A zone must have at least 3 vertices")
        return v


class ZoneResponse(BaseModel):
    id: str
    name: str
    description: str
    coordinates: List[Coordinate]
    color: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
