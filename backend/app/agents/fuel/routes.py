from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.shared.response import build_success_response
from backend.app.agents.fuel.schemas import FuelRequest
from backend.app.agents.fuel.service import FuelService
service = FuelService()

logger = logging.getLogger("agentfleet.agents.fuel.routes")
router = APIRouter()

@router.post("/fuel/plan", tags=["Fuel"])
async def fuel_endpoint(p: FuelRequest, db: Session = Depends(get_db)):
    """
    Plan fuel cost and refuel stops for a trip
    """
    result = service.plan_fuel(db=db, vehicle_id=p.vehicle_id, distance_km=p.distance_km, estimated_fuel_liters=p.estimated_fuel_liters)
    return build_success_response(data=result)

