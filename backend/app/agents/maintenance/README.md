# Maintenance Agent

## Overview

The **Maintenance Agent** is the third agent in the AgentFleet pipeline. It acts as a **Diagnostic Checker** — evaluating the health score of the assigned vehicle, scheduling urgent servicing when required, and notifying the driver by email.

---

## Responsibilities

- Fetch the vehicle record by ID.
- Read the vehicle's `health_score` field.
- Apply **rule-based diagnostics** to classify health status.
- Estimate **remaining safe service distance** before next maintenance.
- If health is critical (`< 50`):
  - Insert a maintenance log record.
  - Set vehicle status to `Maintenance` (removing it from dispatch pool).
  - **Send an HTML email alert to the assigned driver**.
- Return a structured diagnostic report.

---

## API Endpoint

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/maintenance/evaluate` | Evaluate vehicle health and schedule maintenance if needed |

### Request Payload
```json
{
  "vehicle_id": "<uuid>"
}
```

### Response Payload (Healthy)
```json
{
  "status": "success",
  "data": {
    "agent": "Maintenance Agent",
    "vehicle_id": "<uuid>",
    "health_score": 88,
    "vehicle_status": "Healthy",
    "message": "Vehicle is healthy.",
    "next_service_after_km": 1900
  }
}
```

### Response Payload (Critical)
```json
{
  "status": "success",
  "data": {
    "agent": "Maintenance Agent",
    "vehicle_id": "<uuid>",
    "health_score": 35,
    "vehicle_status": "Maintenance Required",
    "message": "Vehicle requires immediate maintenance."
  }
}
```

---

## Health Score Classification Rules

| Score Range | Status | Action Taken |
|-------------|--------|-------------|
| `> 80` | `Healthy` | None — return report only |
| `50 – 80` | `Service Recommended` | Return report with `next_service_after_km` |
| `< 50` | `Maintenance Required` | Log entry inserted, vehicle → `Maintenance`, driver email sent |

**Remaining service distance formula:**
```
remaining_service_distance = (health_score - 50) * 50  km  (valid when score >= 50)
```

---

## Email Alert (Critical Health)

When a vehicle health score drops below 50, the agent:
1. Looks up the current driver via `vehicles → drivers → users` JOIN.
2. If the driver's email ends in `@agentfleet.com` (mock domain), it falls back to `DEMO_DRIVER_EMAIL` from `.env`.
3. Sends an HTML email with:
   - Health score
   - Vehicle plate number
   - Diagnostic issue description
   - Instructions to deliver vehicle to garage

---

## Internal Logic (`service.py`)

```
evaluate_vehicle(vehicle_id)
    │
    ├── 1. get_vehicle(vehicle_id)              → raises VehicleUnavailableException if not found
    ├── 2. get_latest_maintenance(vehicle_id)   → log trace only
    ├── 3. Rule-based health_score classification
    ├── 4. Compute remaining_service_distance
    └── [if critical]:
        ├── 5. insert_maintenance_log()
        ├── 6. update_vehicle_health(status="Maintenance")
        └── 7. send_email_async(driver_email, subject, html_body)
```

---

## Module Files

| File | Purpose |
|------|---------|
| `agent.py` | Agent registry entry — wraps service call |
| `service.py` | Business logic: health scoring rules, maintenance log, email dispatch |
| `repository.py` | Database queries: vehicle fetch, maintenance log insert, health status update |
| `routes.py` | FastAPI router — exposes `POST /maintenance/evaluate` |
| `schemas.py` | Pydantic request/response models |
| `prompts.py` | AI prompt templates |
| `tools.py` | LLM tool definitions |

---

## Shared Utilities Used

| Module | Usage |
|--------|-------|
| `shared.notifications.email` | `send_email_async()` — threaded SMTP email sender |
| `shared.exceptions` | `VehicleUnavailableException` |
| `core.config.settings` | `DEMO_DRIVER_EMAIL` — fallback email for mock driver accounts |

---

## Error Cases

| Condition | Exception Raised | HTTP Code |
|-----------|-----------------|-----------|
| Vehicle not found by ID | `VehicleUnavailableException` | 503 |
| Email delivery failure | Warning logged, execution continues | — |

---

## Notes

- The background scanner `run_autonomous.py` independently polls all vehicles on a schedule — this agent only evaluates a single vehicle per API call.
- A `GET /maintenance` endpoint also exists for listing all maintenance records.
