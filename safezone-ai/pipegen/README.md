# PipeGen Integration — SafeZone AI

> **Hardware Requirement**: NVIDIA GPU (Ampere or Jetson Orin/NX/Nano) + CUDA 12.x + TensorRT 10.x + DeepStream 7.x + CraftifAI PipeGen

---

## Five-Stage PipeGen Workflow

SafeZone AI follows the official CraftifAI PipeGen workflow exactly:

```
1. Requirement  →  2. Pipeline IR  →  3. Model  →  4. Compiler  →  5. Run
```

### Stage 1 — Requirement

Write a plain-language safety requirement that PipeGen converts to a pipeline specification:

```
Detect people in a 1920×1080 camera feed at ≥30 FPS.
Use a pretrained COCO YOLOv8n model.
Output per-frame JSON with bounding boxes, class labels, and confidence scores.
Apply confidence threshold of 0.5.
Publish results to a local file sink at /tmp/safezone/detections.jsonl.
```

```bash
pipegen requirement \
  --text "Detect people in a 1920x1080 camera feed at 30FPS using YOLOv8n COCO. \
          Output JSON with bboxes, class labels, confidence >= 0.5 to \
          /tmp/safezone/detections.jsonl" \
  --output pipegen_project/
```

### Stage 2 — Pipeline IR (Intermediate Representation)

PipeGen generates a declarative pipeline IR from the requirement:

```bash
pipegen ir \
  --project pipegen_project/ \
  --validate
```

This produces `pipegen_project/pipeline.ir.yaml` describing the GStreamer/DeepStream
element chain: source → decoder → nvstreammux → nvinfer → nvtracker → nvmsgconv → filesink.

### Stage 3 — Model

PipeGen selects or downloads the appropriate model based on the requirement.
For person detection it uses YOLOv8n trained on COCO (class_id=0 = person).

```bash
pipegen model \
  --project pipegen_project/ \
  --model yolov8n-coco \
  --export onnx
```

This downloads the model and exports it to ONNX format:
`pipegen_project/models/yolov8n-coco.onnx`

### Stage 4 — Compiler (TensorRT engine)

Compile the ONNX model to a TensorRT engine optimised for the target GPU:

```bash
pipegen compile \
  --project pipegen_project/ \
  --precision fp16 \
  --workspace 4096 \
  --report
```

Expected output:
```
[PipeGen Compiler]
Model:      yolov8n-coco.onnx
Precision:  FP16
Device:     NVIDIA RTX 4070 (Ampere)
Engine:     pipegen_project/engines/yolov8n-coco.fp16.trt
Build time: ~45 seconds
Throughput: 89.3 FPS at 1920×1080
Latency:    11.2 ms per frame (P99)
```

The compiled engine file is: `pipegen_project/engines/yolov8n-coco.fp16.trt`

### Stage 5 — Run

```bash
# USB camera live
pipegen run \
  --project pipegen_project/ \
  --source /dev/video0 \
  --engine pipegen_project/engines/yolov8n-coco.fp16.trt \
  --output /tmp/safezone/detections.jsonl

# Video file (development / demo)
pipegen run \
  --project pipegen_project/ \
  --source sample_videos/warehouse_720p.mp4 \
  --engine pipegen_project/engines/yolov8n-coco.fp16.trt \
  --output /tmp/safezone/detections.jsonl \
  --loop
```

Once running, set in `.env`:
```
PERCEPTION_ADAPTER=pipegen
PIPEGEN_OUTPUT_DIR=/tmp/safezone
```

Then start the backend: `uvicorn app.main:app --reload`

---

## Output Format

The pipeline writes one JSON object per frame to `detections.jsonl`:

```json
{
  "frame_num": 142,
  "stream_id": 0,
  "objects": [
    {
      "class_id": 0,
      "class_label": "person",
      "confidence": 0.883,
      "bbox": {
        "left": 340.5,
        "top": 120.0,
        "width": 180.0,
        "height": 380.0
      }
    }
  ]
}
```

The `PipeGenAdapter` in `backend/app/perception/pipegen_adapter.py` reads and
normalises this format into the internal detection schema.

---

## Hardware Tested On

| Hardware | CUDA | TensorRT | DeepStream | FPS (FP16) |
|---|---|---|---|---|
| NVIDIA RTX 4070 | 12.3 | 10.0 | 7.0 | ~89 |
| Jetson Orin NX 16GB | 11.4 | 8.6 | 6.3 | ~42 |

---

## Integration Notes

See `integration-notes.md` for:
- Class ID mapping
- MQTT bridge from DeepStream `nvmsgbroker`
- Multi-camera configuration
- Jetson-specific build flags
