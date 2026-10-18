# PipeGen Integration Notes

## Adapter Interface

`backend/app/perception/pipegen_adapter.py` connects the SafeZone backend to a
running PipeGen/DeepStream pipeline.

### How it Works

1. The pipeline writes JSON-line objects to `${PIPEGEN_OUTPUT_DIR}/detections.jsonl`.
2. The adapter tails the file asynchronously using a non-blocking reader.
3. Each line is parsed; objects with `class_id=0` or `class_label="person"` and
   confidence ≥ `DETECTION_CONFIDENCE_THRESHOLD` are forwarded.
4. Bounding boxes are normalised to [0,1] using `FRAME_WIDTH`/`FRAME_HEIGHT` env vars
   (default: 1920×1080).
5. Normalised `cx`, `cy` values are computed for zone-entry checks.

### Malformed Event Handling

- `json.JSONDecodeError` → warning logged, line skipped
- Missing `bbox` keys → defaults to 0.0
- Low confidence → silently filtered
- File not yet present → polls every 1 second with a logged warning

## Class ID Mapping

For YOLOv8n-COCO model used in Stage 3:

| Class ID | Label |
|---|---|
| 0 | person |
| 1 | bicycle |
| 2 | car |
| ... | ... |

Only `class_id=0` / `class_label="person"` trigger zone-entry incidents.
To add additional hazardous classes (e.g. forklifts), extend `PERSON_CLASS_IDS`
and `PERSON_CLASS_LABELS` in `pipegen_adapter.py`.

## MQTT Direct from DeepStream

Alternatively, DeepStream's `nvmsgbroker` element can publish directly to the MQTT broker.
Configure in `pipeline.ir.yaml`:

```yaml
msgbroker:
  proto-lib: /opt/nvidia/deepstream/deepstream/lib/libnvds_mqtt_proto.so
  conn-str: "localhost;1883"
  topic: safezone/deepstream
```

The backend can then subscribe to this topic as a second event source.

## Multi-Camera Setup

```bash
pipegen run \
  --project pipegen_project/ \
  --source /dev/video0 /dev/video1 \
  --engine pipegen_project/engines/yolov8n-coco.fp16.trt \
  --output /tmp/safezone/detections.jsonl
```

Each frame JSON includes `stream_id` to identify the camera.

## Jetson Build Flags

```bash
# Build TensorRT engine for Jetson Orin
pipegen compile \
  --project pipegen_project/ \
  --precision fp16 \
  --dla-core 0 \
  --target jetson-orin
```

## Testing the Integration

```bash
# Generate test output matching the pipeline format
python scripts/inject_test_event.py \
  --output /tmp/safezone/detections.jsonl \
  --frames 50
```

See `scripts/inject_test_event.py` for the event injector used in integration tests.
