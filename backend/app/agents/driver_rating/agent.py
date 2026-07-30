from sqlalchemy.orm import Session
import logging
from backend.app.core.base_agent import BaseAgent
from backend.app.agents.driver_rating.service import DriverRatingService

logger = logging.getLogger("agentfleet.agents.driver_rating.agent")

class DriverRatingAgent(BaseAgent):
    def __init__(self, service: DriverRatingService = DriverRatingService()):
        self.service = service
        logger.info("DriverRatingAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        if not task_data.get("driver_id"):
            raise ValueError("'driver_id' is required for driver rating.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        return self.service.rate_driver(
            db=db,
            driver_id=task_data["driver_id"],
        )

    def format_response(self, result: dict) -> dict:
        return {"status": "success", "agent": "Driver Rating Agent", **result}
