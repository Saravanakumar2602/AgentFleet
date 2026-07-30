from sqlalchemy.orm import Session
import logging
from backend.app.core.base_agent import BaseAgent
from backend.app.agents.cargo_validation.service import CargoValidationService

logger = logging.getLogger("agentfleet.agents.cargo_validation.agent")

class CargoValidationAgent(BaseAgent):
    def __init__(self, service: CargoValidationService = CargoValidationService()):
        self.service = service
        logger.info("CargoValidationAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        if not task_data.get("weight"):
            raise ValueError("'weight' is required for cargo validation.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        return self.service.validate_cargo(
            db=db,
            pickup=task_data.get("pickup", ""),
            destination=task_data.get("destination", ""),
            cargo_weight=float(task_data["weight"]),
        )

    def format_response(self, result: dict) -> dict:
        return {"status": "success", "agent": "Cargo Validation Agent", **result}
