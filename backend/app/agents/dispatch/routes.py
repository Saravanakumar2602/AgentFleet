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
    try:
        # Check if vehicles table exists
        db.execute(text("SELECT 1 FROM vehicles LIMIT 1"))
        
        query = text("""
            SELECT v.id, v.vehicle_number, v.vehicle_type, v.capacity_kg, v.fuel_type, v.fuel_level, v.status, v.health_score,
                   u.name as driver_name
            FROM vehicles v
            LEFT JOIN drivers d ON v.current_driver_id = d.id
            LEFT JOIN users u ON d.user_id = u.id
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
                "health_score": float(v_dict["health_score"]) if v_dict["health_score"] is not None else 100.0
            })
        return build_success_response(data=vehicles)
    except Exception as exc:
        logger.warning(f"Database query failed or vehicles table not found: {exc}. Returning default vehicles.")
        # Fallback to standard 6 vehicles matching frontend expected schema
        default_vehicles = [
            { "id": "v1", "number": "TN38AB1234", "type": "Dry Van", "capacity": "3,000 kg", "driver": "Ravi K.", "status": "Available", "health_score": 92 },
            { "id": "v2", "number": "TN38CD5678", "type": "Flatbed", "capacity": "5,000 kg", "driver": "Suresh P.", "status": "Available", "health_score": 75 },
            { "id": "v3", "number": "TN38EF9012", "type": "Reefer", "capacity": "1,500 kg", "driver": "Arun M.", "status": "Busy", "health_score": 96 },
            { "id": "v4", "number": "KA-RT-8011", "type": "Heavy Duty", "capacity": "8,000 kg", "driver": "—", "status": "Available", "health_score": 100 },
            { "id": "v5", "number": "MH12AB3456", "type": "Dry Van", "capacity": "2,500 kg", "driver": "Kiran S.", "status": "Available", "health_score": 85 },
            { "id": "v6", "number": "TN45GH7890", "type": "Flatbed", "capacity": "4,000 kg", "driver": "Priya R.", "status": "Maintenance", "health_score": 45 },
        ]
        return build_success_response(data=default_vehicles)

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

