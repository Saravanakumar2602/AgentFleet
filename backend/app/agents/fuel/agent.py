from sqlalchemy.orm import Session
import logging
from backend.app.core.base_agent import BaseAgent
from backend.app.agents.fuel.service import FuelService

logger = logging.getLogger("agentfleet.agents.fuel.agent")

class FuelAgent(BaseAgent):
    def __init__(self, service: FuelService = FuelService()):
        self.service = service
        logger.info("FuelAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        if not task_data.get("vehicle_id"):
            raise ValueError("'vehicle_id' is required for fuel planning.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        return self.service.plan_fuel(
            db=db,
            vehicle_id=task_data["vehicle_id"],
            distance_km=float(task_data.get("distance_km", 0)),
            estimated_fuel_liters=float(task_data.get("estimated_fuel_liters", 0)),
        )

    def format_response(self, result: dict) -> dict:
        return {"status": "success", "agent": "Fuel Agent", **result}
