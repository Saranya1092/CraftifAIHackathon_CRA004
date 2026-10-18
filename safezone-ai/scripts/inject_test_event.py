#!/usr/bin/env python3
"""
inject_test_event.py
====================
Writes synthetic PipeGen-format JSON lines to a file, simulating a running
DeepStream pipeline.  Used for integration testing and demos.

⚠ OUTPUT IS SIMULATED — NOT REAL AI INFERENCE.

Usage:
  python scripts/inject_test_event.py --output /tmp/safezone/detections.jsonl --frames 50
"""
from __future__ import annotations

import argparse
import json
import math
import os
import time
from datetime import datetime, timezone


def make_frame(frame_num: int) -> dict:
    # Sinusoidal person movement
    cx_norm = (math.sin(frame_num * 0.3) + 1.0) / 2.0
    cy_norm = (math.cos(frame_num * 0.2) + 1.0) / 2.0

    # Convert back to pixel coords for the PipeGen format
    frame_w, frame_h = 1920, 1080
    cx_px = cx_norm * frame_w
    cy_px = cy_norm * frame_h
    w_px, h_px = 180.0, 380.0

    return {
        "frame_num": frame_num,
        "stream_id": 0,
        "objects": [
            {
                "class_id": 0,
                "class_label": "person",
                "confidence": round(0.82 + 0.1 * math.sin(frame_num * 0.7), 3),
                "bbox": {
                    "left": max(0.0, cx_px - w_px / 2),
                    "top": max(0.0, cy_px - h_px / 2),
                    "width": w_px,
                    "height": h_px,
                },
            }
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inject simulated PipeGen events")
    parser.add_argument("--output", default="/tmp/safezone/detections.jsonl")
    parser.add_argument("--frames", type=int, default=30)
    parser.add_argument("--fps", type=float, default=2.0)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    print(f"[inject_test_event] Writing {args.frames} frames to {args.output}")
    print("[inject_test_event] ⚠ SIMULATED output – not real inference")

    with open(args.output, "a", encoding="utf-8") as fh:
        for i in range(1, args.frames + 1):
            frame = make_frame(i)
            fh.write(json.dumps(frame) + "\n")
            fh.flush()
            print(f"  Frame {i}/{args.frames} cx={frame['objects'][0]['bbox']['left']:.0f}")
            time.sleep(1.0 / args.fps)

    print("[inject_test_event] Done.")


if __name__ == "__main__":
    main()
