from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.shared.response import build_success_response
from backend.app.agents.traffic.schemas import TrafficRequest
from backend.app.agents.traffic.service import TrafficService
service = TrafficService()

logger = logging.getLogger("agentfleet.agents.traffic.routes")
router = APIRouter()

@router.post("/traffic/analyze", tags=["Traffic"])
async def traffic_endpoint(p: TrafficRequest, db: Session = Depends(get_db)):
    """
    Analyze traffic conditions for a route
    """
    result = service.analyze_traffic(db=db, pickup=p.pickup, destination=p.destination)
    return build_success_response(data=result)

