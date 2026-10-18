"""SQLAlchemy model for hazard zones."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="")
    # JSON-serialised list of {x, y} dicts
    coordinates_json: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str] = mapped_column(String(20), default="#ef4444")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def coordinates(self) -> List[dict]:
        return json.loads(self.coordinates_json)

    @coordinates.setter
    def coordinates(self, value: List[dict]) -> None:
        self.coordinates_json = json.dumps(value)
