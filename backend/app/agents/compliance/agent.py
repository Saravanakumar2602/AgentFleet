from sqlalchemy.orm import Session
import logging
from backend.app.core.base_agent import BaseAgent
from backend.app.agents.compliance.service import ComplianceService

logger = logging.getLogger("agentfleet.agents.compliance.agent")

class ComplianceAgent(BaseAgent):
    def __init__(self, service: ComplianceService = ComplianceService()):
        self.service = service
        logger.info("ComplianceAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        if not task_data.get("driver_id") or not task_data.get("vehicle_id"):
            raise ValueError("'driver_id' and 'vehicle_id' are required.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        return self.service.check_compliance(
            db=db,
            driver_id=task_data["driver_id"],
            vehicle_id=task_data["vehicle_id"],
        )

    def format_response(self, result: dict) -> dict:
        return {"status": "success", "agent": "Compliance Agent", **result}
