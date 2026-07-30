from sqlalchemy.orm import Session
import logging
from backend.app.core.base_agent import BaseAgent
from backend.app.agents.traffic.service import TrafficService

logger = logging.getLogger("agentfleet.agents.traffic.agent")

class TrafficAgent(BaseAgent):
    def __init__(self, service: TrafficService = TrafficService()):
        self.service = service
        logger.info("TrafficAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        return self.service.analyze_traffic(
            db=db,
            pickup=task_data.get("pickup", ""),
            destination=task_data.get("destination", ""),
        )

    def format_response(self, result: dict) -> dict:
        return {"status": "success", "agent": "Traffic Agent", **result}
