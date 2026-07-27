from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.supabase import get_db
from backend.app.shared.response import success_response, error_response
from backend.app.shared.logger import logger
from backend.app.agents.dispatch.schemas import DispatchRequest

router = APIRouter()

@router.post("/allocate", tags=["Dispatch"])
async def allocate_vehicle(payload: DispatchRequest, db: Session = Depends(get_db)):
    """
    Simulates triggering vehicle allocation logic for a dispatch request.
    """
    logger.info(f"Received dispatch request for load weight: {payload.load_weight} kg")
    try:
        # Placeholder allocation result
        result = {
            "assigned_vehicle_id": "VEH-TEMP-01",
            "driver_id": "DRIVER-TEMP-01",
            "load_weight": payload.load_weight,
            "destination": payload.destination
        }
        return success_response(
            data=result, 
            message="Dispatch allocation processed successfully (simulation)."
        )
    except Exception as e:
        logger.error(f"Error executing dispatch agent: {e}")
        return error_response(message="Failed to allocate vehicle.", error=str(e))
