from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.agents.dispatch.schemas import DispatchRequest, DispatchResponse
from backend.app.agents.dispatch.service import DispatchService, NoSuitableAssetException

logger = logging.getLogger("agentfleet.agents.dispatch.routes")
router = APIRouter()
dispatch_service = DispatchService()

@router.post("/dispatch", response_model=DispatchResponse, tags=["Dispatch"])
async def dispatch_cargo(payload: DispatchRequest, db: Session = Depends(get_db)):
    """
    Exposes POST /dispatch API. Filters assets by capacity, maps closest vehicle coordinates,
    updates database records, and creates a trip.
    """
    try:
        result = dispatch_service.allocate_dispatch(
            db=db,
            pickup=payload.pickup,
            destination=payload.destination,
            cargo_weight=payload.weight
        )
        return DispatchResponse(
            status="success",
            agent="Dispatch Agent",
            trip_id=result["trip_id"],
            vehicle=result["vehicle"],
            driver=result["driver"],
            message="Vehicle assigned successfully."
        )
    except NoSuitableAssetException as e:
        logger.warning(f"Dispatch match failure: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "failed",
                "message": "No suitable vehicle found."
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error matching dispatch: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "failed",
                "message": "Internal service error during asset matching."
            }
        )
