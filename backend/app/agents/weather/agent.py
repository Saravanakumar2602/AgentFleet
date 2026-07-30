from sqlalchemy.orm import Session
import logging
from backend.app.core.base_agent import BaseAgent
from backend.app.agents.weather.service import WeatherService

logger = logging.getLogger("agentfleet.agents.weather.agent")

class WeatherAgent(BaseAgent):
    def __init__(self, service: WeatherService = WeatherService()):
        self.service = service
        logger.info("WeatherAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        if not task_data.get("destination"):
            raise ValueError("'destination' is required for weather check.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        return self.service.get_weather(
            db=db,
            destination=task_data["destination"],
        )

    def format_response(self, result: dict) -> dict:
        return {"status": "success", "agent": "Weather Agent", **result}
