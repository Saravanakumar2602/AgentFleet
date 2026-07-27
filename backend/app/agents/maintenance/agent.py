from sqlalchemy.orm import Session
import logging

from backend.app.agents.maintenance.service import MaintenanceService

logger = logging.getLogger("agentfleet.agents.maintenance.agent")

class MaintenanceAgent:
    """
    Interface layer for the Vehicle Health & Maintenance Agent.
    Bridges backend business logic with future LLM/LangGraph/CrewAI framework entries.
    """
    def __init__(self, service: MaintenanceService = MaintenanceService()):
        self.service = service
        logger.info("MaintenanceAgent initialized.")

    async def execute(self, db: Session, task_data: dict) -> dict:
        """
        Executes the agent logic programmatically.
        Expected task_data schema: {"vehicle_id": str}
        """
        logger.info(f"Agent execution triggered with inputs: {task_data}")
        vehicle_id = task_data.get("vehicle_id")

        if not vehicle_id:
            raise ValueError("Invalid execution inputs. 'vehicle_id' is required.")

        return self.service.evaluate_vehicle(
            db=db,
            vehicle_id=vehicle_id
        )
