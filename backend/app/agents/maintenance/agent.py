from sqlalchemy.orm import Session
import logging

from backend.app.core.base_agent import BaseAgent
from backend.app.agents.maintenance.service import MaintenanceService

logger = logging.getLogger("agentfleet.agents.maintenance.agent")

class MaintenanceAgent(BaseAgent):
    """
    Interface layer for the Vehicle Health & Maintenance Agent.
    Inherits from BaseAgent to participate in multi-agent registries.
    """
    def __init__(self, service: MaintenanceService = MaintenanceService()):
        self.service = service
        logger.info("MaintenanceAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        vehicle_id = task_data.get("vehicle_id")

        if not vehicle_id:
            raise ValueError("Invalid execution inputs. 'vehicle_id' is required.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        vehicle_id = task_data.get("vehicle_id")

        return self.service.evaluate_vehicle(
            db=db,
            vehicle_id=vehicle_id
        )

    def format_response(self, result: dict) -> dict:
        res = {
            "status": "success",
            "agent": "Maintenance Agent",
            "vehicle_id": str(result["vehicle_id"]),
            "health_score": int(result["health_score"]),
            "vehicle_status": result["vehicle_status"],
            "message": result["message"]
        }
        if "next_service_after_km" in result:
            res["next_service_after_km"] = result["next_service_after_km"]
        return res
