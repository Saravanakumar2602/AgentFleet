from sqlalchemy.orm import Session
import logging
from backend.app.core.base_agent import BaseAgent
from backend.app.agents.eta_updater.service import EtaUpdaterService

logger = logging.getLogger("agentfleet.agents.eta_updater.agent")

class EtaUpdaterAgent(BaseAgent):
    def __init__(self, service: EtaUpdaterService = EtaUpdaterService()):
        self.service = service
        logger.info("EtaUpdaterAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        if task_data.get("base_duration_minutes") is None:
            raise ValueError("'base_duration_minutes' is required.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        return self.service.update_eta(
            db=db,
            base_duration_minutes=int(task_data.get("base_duration_minutes", 0)),
            traffic_delay_minutes=int(task_data.get("traffic_delay_minutes", 0)),
            weather_delay_minutes=int(task_data.get("weather_delay_minutes", 0)),
        )

    def format_response(self, result: dict) -> dict:
        return {"status": "success", "agent": "ETA Updater Agent", **result}
