from sqlalchemy.orm import Session
import logging

from backend.app.core.base_agent import BaseAgent
from backend.app.agents.dispatch.service import DispatchService

logger = logging.getLogger("agentfleet.agents.dispatch.agent")

class DispatchAgent(BaseAgent):
    """
    Interface layer for the Dispatch & Allocation Agent.
    Inherits from BaseAgent to participate in multi-agent registries.
    """
    def __init__(self, service: DispatchService = DispatchService()):
        self.service = service
        logger.info("DispatchAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        pickup = task_data.get("pickup")
        destination = task_data.get("destination")
        weight = task_data.get("weight")

        if not all([pickup, destination, weight]):
            raise ValueError("Invalid execution inputs. 'pickup', 'destination', and 'weight' are required.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        pickup = task_data.get("pickup")
        destination = task_data.get("destination")
        weight = task_data.get("weight")

        return self.service.allocate_dispatch(
            db=db,
            pickup=pickup,
            destination=destination,
            cargo_weight=float(weight)
        )

    def format_response(self, result: dict) -> dict:
        return {
            "status": "success",
            "agent": "Dispatch Agent",
            "trip_id": str(result["trip_id"]),
            "vehicle": result["vehicle"],
            "driver": result["driver"]
        }
