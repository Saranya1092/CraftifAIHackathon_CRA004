"""SQLAlchemy model for safety incidents."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "zone_entry"
    zone_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    zone_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="high")  # low/medium/high
    status: Mapped[str] = mapped_column(String(20), default="active")   # active/acknowledged/resolved
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="simulated")  # simulated/pipegen/deepstream
    # JSON detection metadata: bounding box, class, etc.
    detection_metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    frame_timestamp: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    def detection_metadata(self) -> Optional[dict]:
        if self.detection_metadata_json:
            return json.loads(self.detection_metadata_json)
        return None

    @detection_metadata.setter
    def detection_metadata(self, value: Optional[dict]) -> None:
        self.detection_metadata_json = json.dumps(value) if value else None
