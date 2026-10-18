"""Abstract base class for perception adapters."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any


class BaseAdapter(ABC):
    """
    A perception adapter streams batches of detections.

    Each detection is a dict conforming to the internal detection format:
    {
        "class": str | int,          # class label ("person") or index (0)
        "confidence": float,          # 0.0 – 1.0
        "bbox": [x1, y1, x2, y2],    # normalised coordinates in [0,1]
        "cx": float,                  # centre x normalised
        "cy": float,                  # centre y normalised
        "frame_timestamp": str,       # ISO-8601 UTC
        "source": str,               # adapter identifier
    }
    """

    @abstractmethod
    async def stream(self) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """Yield batches of detections indefinitely until cancelled."""
        ...
