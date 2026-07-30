from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.shared.response import build_success_response
from backend.app.agents.invoice.schemas import InvoiceRequest
from backend.app.agents.invoice.service import InvoiceService
service = InvoiceService()

logger = logging.getLogger("agentfleet.agents.invoice.routes")
router = APIRouter()

@router.post("/invoice/generate", tags=["Invoice"])
async def invoice_endpoint(p: InvoiceRequest, db: Session = Depends(get_db)):
    """
    Generate delivery invoice and email to customer
    """
    result = service.generate_invoice(db=db, trip_id=p.trip_id, distance_km=p.distance_km, fuel_cost_inr=p.fuel_cost_inr)
    return build_success_response(data=result)

