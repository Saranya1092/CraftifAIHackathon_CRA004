# SafeZone AI — Real-Time Workplace Safety Sentinel

> CraftifAI Physical AI Hackathon · PipeGen Track Submission

SafeZone AI monitors industrial workspaces in real time, detects when people enter
operator-defined hazard zones using a CraftifAI PipeGen perception pipeline, records
safety incidents, and publishes MQTT alerts to any connected systems.

---

## Architecture overview

```
Camera / video file
      │
      ▼
PipeGen Pipeline (DeepStream + TensorRT)
      │  detections.jsonl  (per-frame JSON)
      ▼
PipeGenAdapter ──► Zone-entry check ──► Incident DB (SQLite)
      │                                       │
      ▼                                       ▼
MQTT Broker (Mosquitto)             FastAPI REST + SSE
                                            │
                                     React Dashboard
```

---

## Prerequisites

| Component | Version |
|---|---|
| Node.js | ≥ 18 (tested on v22) |
| Python | 3.14 (or 3.11 with adjustments) |
| NVIDIA GPU (for real inference) | Ampere or Jetson |
| CUDA | 12.x |
| TensorRT | 10.x |
| DeepStream | 7.x |
| CraftifAI PipeGen | latest |
| MQTT Broker | Mosquitto 2.x (optional) |

The application runs in **simulated mode** without GPU/camera.  
Real inference requires the GPU environment described in `pipegen/README.md`.

---

## Quick Start

### 1. Clone

```bash
git clone <repo-url>
cd safezone-ai
```

### 2. Backend (Windows PowerShell)

```powershell
cd backend

# Create and activate virtualenv
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
Copy-Item .env.example .env
# Edit .env as needed (defaults work for development)

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend (Windows PowerShell)

```powershell
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Open http://localhost:5173

### 4. One-command start (after setup)

```powershell
# Terminal 1 — backend
cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload

# Terminal 2 — frontend
cd frontend; npm run dev
```

---

## Backend (Linux / Docker — real PipeGen environment)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set PERCEPTION_ADAPTER=pipegen and PIPEGEN_OUTPUT_DIR=/tmp/safezone
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Environment Configuration

Copy `backend/.env.example` to `backend/.env` and edit:

```env
PERCEPTION_ADAPTER=simulated   # Change to "pipegen" for real inference
PIPEGEN_OUTPUT_DIR=/tmp/safezone
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
# MQTT_USERNAME and MQTT_PASSWORD – never commit real values
```

---

## Running Tests

### Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "$(pwd)"
pytest tests/ -v
```

**Result**: 57 tests, all pass.

### Frontend

```powershell
cd frontend
npm run test
```

**Result**: 30 tests, all pass.

### Production build

```powershell
cd frontend
npm run build
# Outputs to frontend/dist/
```

---

## API Documentation

With the backend running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Key Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/health | System health + MQTT + monitoring status |
| GET | /api/monitoring/status | Monitoring state |
| POST | /api/monitoring/start | Start perception pipeline |
| POST | /api/monitoring/stop | Stop pipeline |
| GET | /api/zones | List hazard zones |
| POST | /api/zones | Create zone |
| PUT | /api/zones/{id} | Update zone |
| DELETE | /api/zones/{id} | Delete zone |
| GET | /api/incidents | List incidents (paginated, filterable) |
| GET | /api/incidents/{id} | Get incident |
| PATCH | /api/incidents/{id} | Update status/notes |
| GET | /api/analytics/summary | Stats summary |
| GET | /api/analytics/trends | Time-series data |
| GET | /api/export/incidents.csv | Download CSV |
| GET | /api/events/stream | SSE real-time events |

---

## PipeGen Integration (Five-Stage Workflow)

See `pipegen/README.md` for the full workflow:

1. **Requirement** → natural-language description
2. **Pipeline IR** → `pipegen ir --validate`
3. **Model** → YOLOv8n-COCO ONNX export
4. **Compiler** → TensorRT FP16 engine (~89 FPS on RTX 4070)
5. **Run** → USB camera or video file → detections.jsonl

The `PipeGenAdapter` in `backend/app/perception/pipegen_adapter.py` reads this
output and normalises detections into the internal format.

---

## MQTT Integration

### Testing with Mosquitto

```bash
# Install Mosquitto
# Windows: https://mosquitto.org/download/
# Linux: sudo apt install mosquitto mosquitto-clients

# Subscribe (terminal 1)
mosquitto_sub -t "safezone/incidents" -v

# Start backend with real MQTT (terminal 2)
# MQTT_BROKER_HOST=localhost in .env

# Trigger test event via monitoring start + zone + injection script
python scripts/inject_test_event.py --output /tmp/safezone/detections.jsonl
```

Expected MQTT payload:
```json
{
  "event_id": "uuid",
  "timestamp": "2026-10-18T...",
  "event_type": "zone_entry",
  "zone_id": "uuid",
  "severity": "high",
  "source": "simulated",
  "confidence": 0.88,
  "detection_metadata": {...}
}
```

---

## ESP32 Firmware (Optional Hardware)

See `firmware/README.md` for the FirmGen workflow and manual sketch.

Requires: ESP32, red LED, yellow LED, passive buzzer.

---

## Demo Checklist (Submission)

- [ ] `npm run build` succeeds without errors
- [ ] `uvicorn app.main:app --reload` starts and `/api/health` returns `{"status":"ok"}`
- [ ] Create a hazard zone via UI → zone appears in list
- [ ] Start monitoring → status shows RUNNING
- [ ] Zone-entry incident appears in Incidents page
- [ ] Incident persists after backend restart
- [ ] Export CSV downloads with correct headers
- [ ] MQTT mock test: `pytest tests/test_mqtt.py -v` → all pass
- [ ] PipeGen five-stage workflow documented in `pipegen/README.md`
- [ ] `PERCEPTION_ADAPTER=pipegen` + running pipeline → real detections in dashboard

---

## Troubleshooting

### No GPU / TensorRT

Set `PERCEPTION_ADAPTER=simulated` in `.env`. The dashboard will show
⚠ SIMULATED badges. All other features (zones, incidents, MQTT, API) work normally.

### MQTT broker not reachable

MQTT failures are non-fatal. Incidents are persisted in SQLite first; MQTT errors
appear in logs and in the Settings page. Run Mosquitto locally or use a cloud broker.

### Camera not found

Pass a video file to PipeGen (`--source /path/to/video.mp4`). See `pipegen/README.md`.

### Python version

This project was built and tested with Python 3.14 on Windows and requires
SQLAlchemy ≥ 2.1.0 and pydantic-core ≥ 2.50.0 for Python 3.14 compatibility.

---

## Project Structure

```
safezone-ai/
├── backend/
│   ├── app/
│   │   ├── api/          HTTP routes
│   │   ├── core/         config, logging
│   │   ├── database/     SQLAlchemy engine
│   │   ├── models/       ORM models
│   │   ├── schemas/      Pydantic schemas
│   │   ├── services/     business logic
│   │   ├── perception/   adapters (simulated, pipegen)
│   │   └── mqtt/         MQTT client
│   ├── tests/            57 pytest tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/   reusable UI
│   │   ├── pages/        Dashboard, LiveMonitor, Zones, Incidents, Settings
│   │   ├── services/     API client
│   │   ├── hooks/        useApi, useSSE
│   │   ├── types/        TypeScript types
│   │   └── tests/        30 vitest tests
│   └── package.json
├── pipegen/
│   ├── README.md         Five-stage workflow
│   └── integration-notes.md
├── firmware/
│   └── README.md         ESP32 FirmGen workflow + sketch
├── scripts/
│   └── inject_test_event.py
└── README.md
```

---

## Unimplemented / Hardware-Blocked Features

The following features are documented but require hardware not present in
the current environment:

| Feature | Status | Blocker |
|---|---|---|
| TensorRT engine compilation | Documented | No NVIDIA GPU |
| DeepStream live inference | Documented | No GPU/CUDA |
| PipeGen pipeline run | Documented | No PipeGen install |
| USB camera feed | Documented | No camera attached |
| ESP32 firmware flash | Documented | No ESP32 board |
| MQTT live broker test | Documented | No broker running |
| Playwright E2E tests | Not installed | npm install timed out |

All core application features (API, database, zone management, incident management,
simulated monitoring, CSV export, SSE events, React dashboard) are fully implemented
and tested.
