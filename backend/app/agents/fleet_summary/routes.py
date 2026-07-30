from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.shared.response import build_success_response

from backend.app.agents.fleet_summary.service import FleetSummaryService
service = FleetSummaryService()

logger = logging.getLogger("agentfleet.agents.fleet_summary.routes")
router = APIRouter()

@router.get("/fleet/summary", tags=["Fleet Summary"])
async def fleet_summary_endpoint(db: Session = Depends(get_db)):
    """
    Aggregate fleet-wide KPI summary
    """
    result = service.generate_summary(db=db)
    return build_success_response(data=result)

