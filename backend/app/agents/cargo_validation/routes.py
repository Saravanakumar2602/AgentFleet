from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.shared.response import build_success_response
from backend.app.agents.cargo_validation.schemas import CargoValidationRequest
from backend.app.agents.cargo_validation.service import CargoValidationService
service = CargoValidationService()

logger = logging.getLogger("agentfleet.agents.cargo_validation.routes")
router = APIRouter()

@router.post("/cargo/validate", tags=["Cargo Validation"])
async def cargo_validation_endpoint(p: CargoValidationRequest, db: Session = Depends(get_db)):
    """
    Validate cargo weight and classify hazard level
    """
    result = service.validate_cargo(db=db, pickup=p.pickup, destination=p.destination, cargo_weight=p.weight)
    return build_success_response(data=result)

