from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.agents.route.schemas import RouteRequest, RouteResponse
from backend.app.agents.route.service import RouteService
from backend.app.shared.response import build_success_response

logger = logging.getLogger("agentfleet.agents.route.routes")
router = APIRouter()
route_service = RouteService()

@router.post("/route", tags=["Route"])
async def calculate_route(payload: RouteRequest, db: Session = Depends(get_db)):
    """
    Exposes POST /route API. Validates input coordinates, fetches vehicle location,
    computes trip routing details, and saves updates.
    """
    result = route_service.generate_route(
        db=db,
        vehicle_id=payload.vehicle_id,
        pickup=payload.pickup,
        destination=payload.destination
    )

    return build_success_response(
        data={
            "agent": "Route Agent",
            "trip_id": result["trip_id"],
            "distance_km": result["distance_km"],
            "estimated_duration": result["estimated_duration"],
            "estimated_fuel": result["estimated_fuel"]
        },
        message="Route generated successfully."
    )
