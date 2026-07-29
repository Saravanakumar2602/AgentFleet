from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.agents.maintenance.schemas import MaintenanceRequest
from backend.app.agents.maintenance.service import MaintenanceService
from backend.app.shared.response import build_success_response

logger = logging.getLogger("agentfleet.agents.maintenance.routes")
router = APIRouter()
maintenance_service = MaintenanceService()

@router.post("/maintenance", tags=["Maintenance"])
async def check_maintenance(payload: MaintenanceRequest, db: Session = Depends(get_db)):
    """
    Exposes POST /maintenance API. Evaluates vehicle diagnostic score,
    schedules servicing if critical, and returns standardized metrics.
    """
    result = maintenance_service.evaluate_vehicle(
        db=db,
        vehicle_id=payload.vehicle_id
    )
    return build_success_response(
        data=result,
        message=result["message"]
    )

