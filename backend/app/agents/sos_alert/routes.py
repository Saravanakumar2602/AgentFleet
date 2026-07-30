from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.shared.response import build_success_response
from backend.app.agents.sos_alert.schemas import SosAlertRequest
from backend.app.agents.sos_alert.service import SosAlertService
service = SosAlertService()

logger = logging.getLogger("agentfleet.agents.sos_alert.routes")
router = APIRouter()

@router.post("/sos/check", tags=["SOS Alert"])
async def sos_alert_endpoint(p: SosAlertRequest, db: Session = Depends(get_db)):
    """
    Check emergency conditions and alert fleet manager
    """
    result = service.check_and_alert(db=db, weather_risk=p.weather_risk, health_score=p.health_score, vehicle_id=p.vehicle_id, trip_id=p.trip_id)
    return build_success_response(data=result)

