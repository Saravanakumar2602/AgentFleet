from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.agents.dispatch.schemas import DispatchRequest
from backend.app.agents.dispatch.service import DispatchService
from backend.app.shared.response import build_success_response

logger = logging.getLogger("agentfleet.agents.dispatch.routes")
router = APIRouter()
dispatch_service = DispatchService()

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
