from sqlalchemy.orm import Session
import logging
from backend.app.core.base_agent import BaseAgent
from backend.app.agents.sos_alert.service import SosAlertService

logger = logging.getLogger("agentfleet.agents.sos_alert.agent")

class SosAlertAgent(BaseAgent):
    def __init__(self, service: SosAlertService = SosAlertService()):
        self.service = service
        logger.info("SosAlertAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        return self.service.check_and_alert(
            db=db,
            weather_risk=task_data.get("weather_risk", "Low"),
            health_score=int(task_data.get("health_score", 100)),
            vehicle_id=task_data.get("vehicle_id", ""),
            trip_id=task_data.get("trip_id", ""),
        )

    def format_response(self, result: dict) -> dict:
        return {"status": "success", "agent": "SOS Alert Agent", **result}
