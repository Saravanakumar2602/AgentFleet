from sqlalchemy.orm import Session
import logging
from backend.app.core.base_agent import BaseAgent
from backend.app.agents.invoice.service import InvoiceService

logger = logging.getLogger("agentfleet.agents.invoice.agent")

class InvoiceAgent(BaseAgent):
    def __init__(self, service: InvoiceService = InvoiceService()):
        self.service = service
        logger.info("InvoiceAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        if not task_data.get("trip_id"):
            raise ValueError("'trip_id' is required for invoice generation.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        return self.service.generate_invoice(
            db=db,
            trip_id=task_data["trip_id"],
            distance_km=float(task_data.get("distance_km", 0)),
            fuel_cost_inr=float(task_data.get("fuel_cost_inr", 0)),
        )

    def format_response(self, result: dict) -> dict:
        return {"status": "success", "agent": "Invoice Agent", **result}
