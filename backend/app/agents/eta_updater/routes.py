from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.shared.response import build_success_response
from backend.app.agents.eta_updater.schemas import EtaUpdaterRequest
from backend.app.agents.eta_updater.service import EtaUpdaterService
service = EtaUpdaterService()

logger = logging.getLogger("agentfleet.agents.eta_updater.routes")
router = APIRouter()

@router.post("/eta/update", tags=["ETA Updater"])
async def eta_updater_endpoint(p: EtaUpdaterRequest, db: Session = Depends(get_db)):
    """
    Compute adjusted ETA with traffic and weather delays
    """
    result = service.update_eta(db=db, base_duration_minutes=p.base_duration_minutes, traffic_delay_minutes=p.traffic_delay_minutes, weather_delay_minutes=p.weather_delay_minutes)
    return build_success_response(data=result)

