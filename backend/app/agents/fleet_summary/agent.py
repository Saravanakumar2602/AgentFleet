from sqlalchemy.orm import Session
import logging
from backend.app.core.base_agent import BaseAgent
from backend.app.agents.fleet_summary.service import FleetSummaryService

logger = logging.getLogger("agentfleet.agents.fleet_summary.agent")

class FleetSummaryAgent(BaseAgent):
    def __init__(self, service: FleetSummaryService = FleetSummaryService()):
        self.service = service
        logger.info("FleetSummaryAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        return self.service.generate_summary(db=db)

    def format_response(self, result: dict) -> dict:
        return {"status": "success", "agent": "Fleet Summary Agent", **result}
