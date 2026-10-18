"""
demo_api.py — Exercises the SafeZone AI REST API end-to-end and prints
              coloured, readable output showing every major feature.

Run:  python scripts/demo_api.py
Requires: requests  (pip install requests)
"""
import json
import sys
import time
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api"


def req(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if data else {}
    rq = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(rq, timeout=8) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"ERROR": e.code, "detail": e.read().decode()}


def sep(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


# ── 1. Health ────────────────────────────────────────────────────────────────
sep("1. GET /api/health")
h = req("GET", "/health")
print(f"  status   : {h['status']}")
print(f"  version  : {h['version']}")
m = h['monitoring']
print(f"  monitoring status : {m['status']}  (adapter = {m['adapter']})")
print(f"  mqtt connected    : {h['mqtt']['connected']}  broker={h['mqtt']['broker']}")

# ── 2. Create hazard zones ───────────────────────────────────────────────────
sep("2. POST /api/zones — create 2 zones")

z1 = req("POST", "/zones", {
    "name": "Press Machine Area",
    "description": "Around the hydraulic press",
    "coordinates": [{"x": 0.05, "y": 0.05}, {"x": 0.45, "y": 0.05},
                    {"x": 0.45, "y": 0.55}, {"x": 0.05, "y": 0.55}],
    "color": "#ef4444", "is_active": True
})
print(f"  ✓ Zone 1: '{z1['name']}' | id={z1['id'][:8]}… | active={z1['is_active']}")

z2 = req("POST", "/zones", {
    "name": "Conveyor Belt Zone",
    "description": "Near the main conveyor",
    "coordinates": [{"x": 0.55, "y": 0.1}, {"x": 0.95, "y": 0.1},
                    {"x": 0.95, "y": 0.6}, {"x": 0.55, "y": 0.6}],
    "color": "#f59e0b", "is_active": True
})
print(f"  ✓ Zone 2: '{z2['name']}' | id={z2['id'][:8]}… | active={z2['is_active']}")

# ── 3. List zones ────────────────────────────────────────────────────────────
sep("3. GET /api/zones")
zones = req("GET", "/zones")
for z in zones:
    status = "ACTIVE" if z["is_active"] else "DISABLED"
    print(f"  [{status:8}] {z['name']:<25} {len(z['coordinates'])} vertices  color={z['color']}")

# ── 4. Update a zone ─────────────────────────────────────────────────────────
sep("4. PUT /api/zones/{id} — rename zone 1")
updated = req("PUT", f"/zones/{z1['id']}", {"name": "Press Machine Area (Updated)"})
print(f"  ✓ New name: '{updated['name']}'")

# ── 5. Start monitoring ──────────────────────────────────────────────────────
sep("5. POST /api/monitoring/start")
start_r = req("POST", "/monitoring/start")
print(f"  ✓ {start_r['message']}  status={start_r['status']}")
time.sleep(3)   # let simulated adapter generate detections

# ── 6. Monitoring status ─────────────────────────────────────────────────────
sep("6. GET /api/monitoring/status")
ms = req("GET", "/monitoring/status")
print(f"  status           : {ms['status']}")
print(f"  adapter          : {ms['adapter']}")
print(f"  total_detections : {ms['total_detections']}")
print(f"  start_time       : {ms['start_time']}")

# ── 7. Wait a bit more and check incidents ────────────────────────────────────
time.sleep(5)
sep("7. GET /api/incidents (after ~8s of simulated monitoring)")
inc_r = req("GET", "/incidents?page=1&page_size=5")
print(f"  total incidents  : {inc_r['total']}")
print(f"  total pages      : {inc_r['total_pages']}")
for inc in inc_r["items"]:
    conf = f"{inc['confidence']*100:.0f}%" if inc["confidence"] else "n/a"
    print(f"  [{inc['status']:12}] {inc['event_type']:<12} zone='{inc['zone_name'] or '—':<25}' "
          f"severity={inc['severity']:<6} conf={conf}  src={inc['source']}")

# ── 8. Acknowledge an incident ───────────────────────────────────────────────
if inc_r["items"]:
    first_id = inc_r["items"][0]["id"]
    sep(f"8. PATCH /api/incidents/{first_id[:8]}… — acknowledge")
    ack = req("PATCH", f"/incidents/{first_id}",
              {"status": "acknowledged", "acknowledged_by": "operator@safezone.ai",
               "notes": "Investigated – no immediate hazard"})
    print(f"  ✓ status     : {ack['status']}")
    print(f"  ✓ acked by   : {ack['acknowledged_by']}")
    print(f"  ✓ notes      : {ack['notes']}")

# ── 9. Analytics summary ─────────────────────────────────────────────────────
sep("9. GET /api/analytics/summary")
s = req("GET", "/analytics/summary")
print(f"  total_people_detected : {s['total_people_detected']}")
print(f"  total_incidents       : {s['total_incidents']}")
print(f"  active_incidents      : {s['active_incidents']}")
print(f"  acknowledged          : {s['acknowledged_incidents']}")
print(f"  resolved              : {s['resolved_incidents']}")
print(f"  active_zones          : {s['active_zones']}")
print(f"  monitoring_status     : {s['monitoring_status']}")

# ── 10. Analytics trends ──────────────────────────────────────────────────────
sep("10. GET /api/analytics/trends?period=24h")
tr = req("GET", "/analytics/trends?period=24h")
non_zero = [(p["timestamp"][:16], p["incidents"]) for p in tr["data"] if p["incidents"] > 0]
print(f"  period : {tr['period']}")
print(f"  buckets with incidents:")
for ts, cnt in non_zero:
    print(f"    {ts}  →  {cnt} incident(s)")
if not non_zero:
    print("    (none yet — incidents are in the current hour bucket)")

# ── 11. CSV export preview ────────────────────────────────────────────────────
sep("11. GET /api/export/incidents.csv (first 3 lines)")
url = BASE + "/export/incidents.csv"
with urllib.request.urlopen(url, timeout=8) as resp:
    lines = resp.read().decode().strip().split("\n")
for line in lines[:3]:
    print(f"  {line}")

# ── 12. Stop monitoring ───────────────────────────────────────────────────────
sep("12. POST /api/monitoring/stop")
stop_r = req("POST", "/monitoring/stop")
print(f"  ✓ {stop_r['message']}  status={stop_r['status']}")

# ── 13. Delete zone 2 ────────────────────────────────────────────────────────
sep("13. DELETE /api/zones/{id} — remove Conveyor Belt Zone")
del_rq = urllib.request.Request(BASE + f"/zones/{z2['id']}", method="DELETE")
with urllib.request.urlopen(del_rq, timeout=8) as resp:
    print(f"  ✓ HTTP {resp.status} — zone deleted")
remaining = req("GET", "/zones")
print(f"  Zones remaining: {len(remaining)}")

# ── Done ──────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SafeZone AI demo complete.")
print(f"  Dashboard: http://localhost:5173")
print(f"  API docs : http://localhost:8000/docs")
print("="*60 + "\n")
