"""
PipeGen / DeepStream perception adapter.

This adapter connects to the JSON metadata output produced by a CraftifAI
PipeGen-generated DeepStream pipeline.  The pipeline must be compiled and
running separately (see pipegen/README.md and pipegen/integration-notes.md).

How PipeGen output works (from official docs)
---------------------------------------------
A PipeGen-generated pipeline writes per-frame JSON objects to a configurable
output sink (file, socket, or stdout).  Each object has this shape:

  {
    "frame_num": int,
    "stream_id": int,
    "objects": [
      {
        "class_id": int,
        "class_label": str,
        "confidence": float,
        "bbox": {"left": float, "top": float, "width": float, "height": float}
      }
    ]
  }

The class labels and IDs are determined by the model's labels file.
For YOLOv8n-coco, class_id=0 is "person".

The adapter:
  1. Watches a configurable FIFO/socket path for JSON lines.
  2. Parses each line into the internal detection format.
  3. Normalises bounding boxes relative to the configured frame dimensions.
  4. Filters by confidence threshold and person class.
  5. Propagates parse errors as warnings; never crashes the main loop.

HARDWARE REQUIREMENT
--------------------
This adapter requires:
  - NVIDIA GPU (Ampere or later) or NVIDIA Jetson
  - CUDA 12.x + TensorRT 10.x
  - DeepStream 7.x
  - CraftifAI PipeGen installed in the DeepStream container
See pipegen/README.md for the five-stage workflow.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Any, List

from app.core.config import settings
from app.perception.base_adapter import BaseAdapter

logger = logging.getLogger(__name__)

# Default frame dimensions used for bbox normalisation.
# Override with env vars FRAME_WIDTH / FRAME_HEIGHT.
FRAME_WIDTH = int(os.environ.get("FRAME_WIDTH", "1920"))
FRAME_HEIGHT = int(os.environ.get("FRAME_HEIGHT", "1080"))

# Class IDs treated as "person" – extend as needed for your model
PERSON_CLASS_IDS = {0}
PERSON_CLASS_LABELS = {"person", "pedestrian"}


class PipeGenAdapter(BaseAdapter):
    """
    Reads JSON-line output from a running DeepStream/PipeGen pipeline.

    The output path is a named pipe or regular file written by the pipeline's
    nvmsgconv → filesink element.  Set PIPEGEN_OUTPUT_DIR in .env to point to
    the directory where the pipeline writes its output.
    """

    def __init__(self) -> None:
        self._output_dir = settings.pipegen_output_dir
        self._threshold = settings.detection_confidence_threshold

    async def stream(self) -> AsyncGenerator[List[Dict[str, Any]], None]:
        output_path = os.path.join(self._output_dir, "detections.jsonl")
        logger.info("PipeGen adapter watching: %s", output_path)

        # Wait until the pipeline creates its output file
        wait_logged = False
        while not os.path.exists(output_path):
            if not wait_logged:
                logger.warning(
                    "PipeGen output not found at %s – waiting for pipeline to start.",
                    output_path,
                )
                wait_logged = True
            await asyncio.sleep(1.0)

        logger.info("PipeGen output found; streaming detections.")
        async with await asyncio.open_connection() if False else self._open_file(output_path) as reader:
            async for line in reader:
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                    detections = self._parse_frame(raw)
                    if detections:
                        yield detections
                except json.JSONDecodeError as exc:
                    logger.warning("Malformed JSON from pipeline: %s – line: %r", exc, line[:120])
                except Exception as exc:
                    logger.warning("Unexpected pipeline parse error: %s", exc)

    class _open_file:
        """Async context manager that tails a file line-by-line."""

        def __init__(self, path: str) -> None:
            self._path = path
            self._fh = None

        async def __aenter__(self):
            self._fh = open(self._path, "r", encoding="utf-8")  # noqa: WPS515
            return self

        async def __aexit__(self, *_):
            if self._fh:
                self._fh.close()

        def __aiter__(self):
            return self

        async def __anext__(self) -> str:
            while True:
                line = self._fh.readline()  # type: ignore[union-attr]
                if line:
                    return line
                await asyncio.sleep(0.05)

    def _parse_frame(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        detections = []
        frame_ts = datetime.now(timezone.utc).isoformat()

        for obj in raw.get("objects", []):
            cid = obj.get("class_id")
            clabel = str(obj.get("class_label", "")).lower()
            conf = float(obj.get("confidence", 0.0))

            if conf < self._threshold:
                continue
            if cid not in PERSON_CLASS_IDS and clabel not in PERSON_CLASS_LABELS:
                continue

            bbox_raw = obj.get("bbox", {})
            left = float(bbox_raw.get("left", 0)) / FRAME_WIDTH
            top = float(bbox_raw.get("top", 0)) / FRAME_HEIGHT
            width = float(bbox_raw.get("width", 0)) / FRAME_WIDTH
            height = float(bbox_raw.get("height", 0)) / FRAME_HEIGHT
            x1, y1 = max(0.0, left), max(0.0, top)
            x2, y2 = min(1.0, left + width), min(1.0, top + height)
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

            detections.append({
                "class": clabel or "person",
                "confidence": conf,
                "bbox": [x1, y1, x2, y2],
                "cx": cx,
                "cy": cy,
                "frame_timestamp": frame_ts,
                "frame_num": raw.get("frame_num"),
                "stream_id": raw.get("stream_id"),
                "source": "pipegen",
            })

        return detections
