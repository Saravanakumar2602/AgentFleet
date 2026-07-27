from sqlalchemy.orm import Session
import logging

from backend.app.core.base_agent import BaseAgent
from backend.app.agents.route.service import RouteService

logger = logging.getLogger("agentfleet.agents.route.agent")

class RouteAgent(BaseAgent):
    """
    Interface layer for the Route Intelligence Agent.
    Inherits from BaseAgent to participate in multi-agent registries.
    """
    def __init__(self, service: RouteService = RouteService()):
        self.service = service
        logger.info("RouteAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        vehicle_id = task_data.get("vehicle_id")
        pickup = task_data.get("pickup")
        destination = task_data.get("destination")

        if not all([vehicle_id, pickup, destination]):
            raise ValueError("Invalid execution inputs. 'vehicle_id', 'pickup', and 'destination' are required.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        vehicle_id = task_data.get("vehicle_id")
        pickup = task_data.get("pickup")
        destination = task_data.get("destination")

        return self.service.generate_route(
            db=db,
            vehicle_id=vehicle_id,
            pickup=pickup,
            destination=destination
        )

    def format_response(self, result: dict) -> dict:
        return {
            "status": "success",
            "agent": "Route Agent",
            "trip_id": str(result["trip_id"]),
            "distance_km": result["distance_km"],
            "estimated_duration": result["estimated_duration"],
            "estimated_fuel": result["estimated_fuel"]
        }
