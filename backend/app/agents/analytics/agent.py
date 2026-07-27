from sqlalchemy.orm import Session
import logging

from backend.app.core.base_agent import BaseAgent
from backend.app.agents.analytics.service import AnalyticsService

logger = logging.getLogger("agentfleet.agents.analytics.agent")

class AnalyticsAgent(BaseAgent):
    """
    Interface layer for the Fleet Analytics & Optimization Agent.
    Inherits from BaseAgent to participate in multi-agent registries.
    """
    def __init__(self, service: AnalyticsService = AnalyticsService()):
        self.service = service
        logger.info("AnalyticsAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        vehicle_id = task_data.get("vehicle_id")

        if not vehicle_id:
            raise ValueError("Invalid execution inputs. 'vehicle_id' is required.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        vehicle_id = task_data.get("vehicle_id")

        return self.service.generate_report(
            db=db,
            vehicle_id=vehicle_id
        )

    def format_response(self, result: dict) -> dict:
        return {
            "status": "success",
            "agent": "Fleet Analytics Agent",
            "vehicle": result["vehicle"],
            "total_trips": result["total_trips"],
            "average_distance": result["average_distance"],
            "fuel_efficiency": result["fuel_efficiency"],
            "maintenance_count": result["maintenance_count"],
            "utilization": result["utilization"],
            "recommendation": result["recommendation"]
        }
