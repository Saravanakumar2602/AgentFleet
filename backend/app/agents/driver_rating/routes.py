from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.shared.response import build_success_response
from backend.app.agents.driver_rating.schemas import DriverRatingRequest
from backend.app.agents.driver_rating.service import DriverRatingService
service = DriverRatingService()

logger = logging.getLogger("agentfleet.agents.driver_rating.routes")
router = APIRouter()

@router.post("/driver/rate", tags=["Driver Rating"])
async def driver_rating_endpoint(p: DriverRatingRequest, db: Session = Depends(get_db)):
    """
    Score driver performance from trip history
    """
    result = service.rate_driver(db=db, driver_id=p.driver_id)
    return build_success_response(data=result)

