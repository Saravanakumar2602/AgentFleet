from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.shared.response import build_success_response
from backend.app.agents.compliance.schemas import ComplianceRequest
from backend.app.agents.compliance.service import ComplianceService
service = ComplianceService()

logger = logging.getLogger("agentfleet.agents.compliance.routes")
router = APIRouter()

@router.post("/compliance/check", tags=["Compliance"])
async def compliance_endpoint(p: ComplianceRequest, db: Session = Depends(get_db)):
    """
    Check driver regulatory hours and vehicle service compliance
    """
    result = service.check_compliance(db=db, driver_id=p.driver_id, vehicle_id=p.vehicle_id)
    return build_success_response(data=result)

