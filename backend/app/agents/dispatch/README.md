# Dispatch Agent

## Overview

The **Dispatch Agent** is the first agent in the AgentFleet pipeline. It acts as a **Fleet Assigner** — receiving a cargo delivery request and allocating the best available vehicle and driver to that trip.

---

## Responsibilities

- Query available **drivers** and **vehicles** from the database.
- Filter vehicles by **cargo weight capacity** (`capacity_kg >= cargo_weight`).
- Select the **nearest suitable vehicle** to the pickup location using the Haversine distance formula.
- If coordinates are unavailable, fall back to the first capacity-matching vehicle.
- Assign the **first available driver** to the selected vehicle.
- Create a new **trip record** in the database.
- Set the assigned vehicle and driver status to `Busy`.

---

## API Endpoint

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/dispatch/allocate` | Allocate a driver and vehicle for a new delivery |

### Request Payload
```json
{
  "pickup": "chennai",
  "destination": "bangalore",
  "cargo_weight": 2500
}
```

### Response Payload
```json
{
  "status": "success",
  "data": {
    "trip_id": "<uuid>",
    "vehicle": { "id": "<uuid>", "vehicle_number": "KA-01-AA-1234" },
    "driver":  { "id": "<uuid>", "name": "Speedy Gonzales" }
  }
}
```

---

## Internal Logic (`service.py`)

```
allocate_dispatch(pickup, destination, cargo_weight)
    │
    ├── 1. get_available_drivers()        → raises DriverUnavailableException if none
    ├── 2. get_available_vehicles()       → raises VehicleUnavailableException if none
    ├── 3. Filter: capacity_kg >= cargo_weight
    ├── 4. parse_coordinates(pickup)      → pick nearest vehicle by haversine_distance()
    ├── 5. Assign first available driver
    ├── 6. haversine_distance() + estimate_eta() → computes route distance & duration
    └── 7. create_trip() + update_vehicle_status("Busy") + update_driver_status("Busy")
```

---

## Module Files

| File | Purpose |
|------|---------|
| `agent.py` | Agent registry entry — wraps service call |
| `service.py` | Business logic: capacity filtering, nearest-vehicle selection, trip creation |
| `repository.py` | Database queries: drivers, vehicles, trip insert, status updates |
| `routes.py` | FastAPI router — exposes `POST /dispatch/allocate` |
| `schemas.py` | Pydantic request/response models |
| `prompts.py` | AI prompt templates (for LLM-driven dispatch variants) |
| `tools.py` | LLM tool definitions |

---

## Shared Utilities Used

| Module | Usage |
|--------|-------|
| `shared.geo.coordinates` | `parse_coordinates()` — city name → lat/lon |
| `shared.geo.distance` | `haversine_distance()` — great-circle distance |
| `shared.geo.eta` | `estimate_eta()` — travel time at 45 km/h |
| `shared.exceptions` | `DriverUnavailableException`, `VehicleUnavailableException` |

---

## Error Cases

| Condition | Exception Raised | HTTP Code |
|-----------|-----------------|-----------|
| No drivers with `Available` status | `DriverUnavailableException` | 503 |
| No vehicles with `Available` status | `VehicleUnavailableException` | 503 |
| No vehicle meets cargo weight requirement | `VehicleUnavailableException` | 503 |

---

## Notes

- A driver is considered available only if their database `status` column is exactly `'Available'`.
- Both driver and vehicle must be `Available` simultaneously — there is no partial matching.
- To reset availability during testing, visit: `GET http://localhost:8000/health/reset`
