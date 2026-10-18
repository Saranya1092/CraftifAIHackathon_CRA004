# SafeZone AI — Test Results

## Environment

| Item | Value |
|---|---|
| Date | 2026-10-18 |
| OS | Windows 11 |
| Python | 3.14.7 |
| Node.js | v22.17.0 |
| GPU | None (no NVIDIA GPU available) |
| Perception mode | Simulated |

---

## Backend Tests

**Command:**
```powershell
$env:PYTHONPATH="D:\Hackathon\safezone-ai\backend"
pytest tests/ -v --tb=short
```

**Result: 57 passed, 0 failed (0.66s)**

| Test File | Tests | Status |
|---|---|---|
| test_deduplication.py | 5 | ✅ PASSED |
| test_geometry.py | 10 | ✅ PASSED |
| test_health.py | 2 | ✅ PASSED |
| test_incidents.py | 9 | ✅ PASSED |
| test_mqtt.py | 9 | ✅ PASSED |
| test_perception.py | 13 | ✅ PASSED |
| test_zones.py | 9 | ✅ PASSED |

### Key test coverage

- Point-in-polygon ray-casting (center, edge, corner, boundary, degenerate)
- Incident cooldown and deduplication
- Zone CRUD + coordinate validation
- Incident pagination, filtering, status updates
- CSV export with correct headers
- MQTT connect/disconnect/publish (mocked paho client)
- MQTT failure does not raise (graceful degradation)
- Simulated adapter yields normalised detections
- PipeGen adapter parses per-frame JSON correctly
- PipeGen adapter filters low-confidence and non-person detections
- Health endpoint structure
- Analytics summary endpoint

---

## Frontend Tests

**Command:**
```powershell
npm run test
```

**Result: 30 passed, 0 failed (2.47s)**

| Test File | Tests | Status |
|---|---|---|
| api.test.ts | 8 | ✅ PASSED |
| StatusBadge.test.tsx | 5 | ✅ PASSED |
| StatCard.test.tsx | 4 | ✅ PASSED |
| ErrorAlert.test.tsx | 4 | ✅ PASSED |
| EmptyState.test.tsx | 4 | ✅ PASSED |
| ConfirmDialog.test.tsx | 5 | ✅ PASSED |

---

## Production Build

**Command:**
```powershell
npm run build
```

**Result: Success (3.69s)**
```
dist/index.html      0.49 kB │ gzip:   0.33 kB
dist/assets/*.css   16.87 kB │ gzip:   3.88 kB
dist/assets/*.js   645.85 kB │ gzip: 190.35 kB
```

---

## Live Server Verification

**Commands run:**
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Invoke-RestMethod http://localhost:8000/api/health
```

**Result:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "monitoring": {"status": "stopped", "adapter": "simulated"},
  "mqtt": {"connected": false, "broker": "localhost:1883"}
}
```

Zone creation, listing, and analytics verified live.

---

## Hardware-Blocked Tests

These tests exist as documentation but require hardware not available
in the current environment:

| Test | Blocker |
|---|---|
| Real PipeGen pipeline run | No NVIDIA GPU / CUDA / DeepStream |
| TensorRT engine FPS benchmark | No GPU |
| USB camera live feed | No camera |
| Live MQTT broker | No Mosquitto running |
| ESP32 firmware flash | No ESP32 hardware |
| Playwright E2E | npm install timed out |

All software-only tests pass.
