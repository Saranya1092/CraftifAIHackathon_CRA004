"""
Simulated perception adapter.

⚠ THIS IS A SIMULATED/FAKE ADAPTER FOR TESTING AND UI DEVELOPMENT ONLY.
   Results do NOT represent real AI inference.
   Do not use outputs from this adapter as evidence of actual detection.
"""
from __future__ import annotations

import asyncio
import math
import random
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Any, List

from app.perception.base_adapter import BaseAdapter


class SimulatedAdapter(BaseAdapter):
    """
    Deterministic-enough fake event source for automated tests and UI demos.

    Produces person detections that wander sinusoidally across the frame so
    zone-entry events are predictable without requiring a GPU.
    """

    def __init__(self, fps: float = 2.0, seed: int = 42) -> None:
        self._fps = fps
        self._rng = random.Random(seed)
        self._frame = 0

    async def stream(self) -> AsyncGenerator[List[Dict[str, Any]], None]:
        interval = 1.0 / self._fps
        while True:
            self._frame += 1
            detections = self._generate_frame(self._frame)
            yield detections
            await asyncio.sleep(interval)

    def _generate_frame(self, frame_idx: int) -> List[Dict[str, Any]]:
        # One person moving in a sine path across the frame
        cx = (math.sin(frame_idx * 0.3) + 1.0) / 2.0
        cy = (math.cos(frame_idx * 0.2) + 1.0) / 2.0
        # Bounding box ~10% of frame
        half_w, half_h = 0.05, 0.10
        x1 = max(0.0, cx - half_w)
        y1 = max(0.0, cy - half_h)
        x2 = min(1.0, cx + half_w)
        y2 = min(1.0, cy + half_h)
        confidence = round(0.75 + self._rng.uniform(-0.1, 0.15), 3)
        return [
            {
                "class": "person",
                "confidence": min(1.0, confidence),
                "bbox": [x1, y1, x2, y2],
                "cx": cx,
                "cy": cy,
                "frame_timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "simulated",
                "frame_index": frame_idx,
            }
        ]
