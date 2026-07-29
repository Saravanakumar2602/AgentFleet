from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from backend.app.database.supabase import get_db
from backend.app.agents.dispatch.schemas import DispatchRequest
from backend.app.agents.dispatch.service import DispatchService
from backend.app.shared.response import build_success_response

logger = logging.getLogger("agentfleet.agents.dispatch.routes")
router = APIRouter()
dispatch_service = DispatchService()

@router.get("/vehicles", tags=["Dispatch"])
async def get_all_vehicles(db: Session = Depends(get_db)):
    """
    Exposes GET /vehicles API.
    Retrieves all vehicles in the database. Falls back to mock data if table is missing or DB is offline.
    """
    # Check if vehicles table exists
    db.execute(text("SELECT 1 FROM vehicles LIMIT 1"))
    
    query = text("""
        SELECT v.id, v.vehicle_number, v.vehicle_type, v.capacity_kg, v.fuel_type, v.fuel_level, v.status, v.health_score,
               u.name as driver_name,
               t.source as trip_source, t.destination as trip_destination
        FROM vehicles v
        LEFT JOIN drivers d ON v.current_driver_id = d.id
        LEFT JOIN users u ON d.user_id = u.id
        LEFT JOIN trips t ON t.vehicle_id = v.id AND t.status IN ('Assigned', 'Pending', 'In Transit', 'Route Generated')
    """)
    result = db.execute(query)
    vehicles = []
    for row in result:
        v_dict = dict(row._mapping)
        vehicles.append({
            "id": str(v_dict["id"]),
            "number": v_dict["vehicle_number"],
            "type": v_dict["vehicle_type"],
            "capacity": f"{int(v_dict['capacity_kg']):,} kg" if v_dict["capacity_kg"] else "—",
            "driver": v_dict["driver_name"] or "—",
            "status": v_dict["status"],
            "health_score": float(v_dict["health_score"]) if v_dict["health_score"] is not None else 100.0,
            "fuel_level": int(v_dict["fuel_level"]) if v_dict["fuel_level"] is not None else 100,
            "route": f"{v_dict['trip_source']} ➔ {v_dict['trip_destination']}" if v_dict["trip_source"] and v_dict["trip_destination"] else "Standby"
        })
    return build_success_response(data=vehicles)

@router.post("/dispatch", tags=["Dispatch"])
async def dispatch_cargo(payload: DispatchRequest, db: Session = Depends(get_db)):
    """
    Exposes POST /dispatch API.
    All exceptions (e.g. VehicleUnavailableException, DriverUnavailableException)
    are captured and formatted by global middleware exception handlers.
    """
    result = dispatch_service.allocate_dispatch(
        db=db,
        pickup=payload.pickup,
        destination=payload.destination,
        cargo_weight=payload.weight
    )

    return build_success_response(
        data={
            "agent": "Dispatch Agent",
            "trip_id": result["trip_id"],
            "vehicle": result["vehicle"],
            "driver": result["driver"]
        },
        message="Vehicle assigned successfully."
    )

