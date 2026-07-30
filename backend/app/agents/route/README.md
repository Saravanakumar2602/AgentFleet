# Route Agent

## Overview

The **Route Agent** is the second agent in the AgentFleet pipeline. It acts as **Route Intelligence** — taking the trip created by the Dispatch Agent and computing precise routing metrics including distance, estimated travel time, and fuel consumption.

---

## Responsibilities

- Validate and parse **pickup** and **destination** coordinates.
- Verify that the assigned vehicle has a location registry entry.
- Look up the active trip linked to the vehicle.
- Calculate **Haversine great-circle distance** between pickup and destination.
- Estimate **travel time** using configurable speed settings.
- Estimate **fuel consumption** using a configurable consumption rate.
- Update the trip record status to `Route Generated`.

---

## API Endpoint

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/route/generate` | Generate route metrics for an active trip |

### Request Payload
```json
{
  "vehicle_id": "<uuid>",
  "pickup": "13.0827,80.2707",
  "destination": "12.9715,77.5945"
}
```

### Response Payload
```json
{
  "status": "success",
  "data": {
    "trip_id": "<uuid>",
    "distance_km": 347.2,
    "estimated_duration": "7h 42m",
    "estimated_fuel": 24.3
  }
}
```

---

## Internal Logic (`service.py`)

```
generate_route(vehicle_id, pickup, destination)
    │
    ├── 1. parse_coordinates(pickup)       → raises InvalidCoordinateException if invalid
    ├── 2. parse_coordinates(destination)  → raises InvalidCoordinateException if invalid
    ├── 3. get_vehicle_location(vehicle_id)→ raises VehicleUnavailableException if not found
    ├── 4. get_trip(vehicle_id)            → raises AgentFleetException if no active trip
    ├── 5. haversine_distance(p_lat, p_lon, d_lat, d_lon) → distance_km
    ├── 6. estimate_eta(distance_km, speed_kmh=settings.ROUTE_DEFAULT_SPEED_KMH) → minutes
    ├── 7. estimate_fuel(distance_km, fuel_rate_l_100km=settings.ROUTE_FUEL_L_PER_100KM) → liters
    └── 8. update_trip_route(trip_id, distance_km, estimated_duration, status="Route Generated")
```

---

## Configuration Parameters

| Setting | Source | Default |
|---------|--------|---------|
| `ROUTE_DEFAULT_SPEED_KMH` | `core/config.py` | `45.0` km/h |
| `ROUTE_FUEL_L_PER_100KM` | `core/config.py` | `7.0` L/100km |

---

## Module Files

| File | Purpose |
|------|---------|
| `agent.py` | Agent registry entry — wraps service call |
| `service.py` | Business logic: coordinate validation, Haversine calc, fuel & ETA estimation |
| `repository.py` | Database queries: vehicle location lookup, active trip retrieval, route update |
| `routes.py` | FastAPI router — exposes `POST /route/generate` |
| `schemas.py` | Pydantic request/response models |
| `prompts.py` | AI prompt templates |
| `tools.py` | LLM tool definitions |

---

## Shared Utilities Used

| Module | Usage |
|--------|-------|
| `shared.geo.coordinates` | `parse_coordinates()` — city name or `lat,lon` string → tuple |
| `shared.geo.distance` | `haversine_distance()` — great-circle distance in km |
| `shared.geo.eta` | `estimate_eta()` — minutes for given distance and speed |
| `shared.geo.fuel` | `estimate_fuel()` — liters consumed at given rate |
| `shared.exceptions` | `InvalidCoordinateException`, `VehicleUnavailableException`, `AgentFleetException` |

---

## Error Cases

| Condition | Exception Raised | HTTP Code |
|-----------|-----------------|-----------|
| Invalid pickup/destination coordinates | `InvalidCoordinateException` | 422 |
| Vehicle ID not in location registry | `VehicleUnavailableException` | 503 |
| No `Assigned`/`Pending` trip found for vehicle | `AgentFleetException` | 400 |
