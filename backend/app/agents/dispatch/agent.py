from sqlalchemy.orm import Session
import logging

from backend.app.agents.dispatch.service import DispatchService

logger = logging.getLogger("agentfleet.agents.dispatch.agent")

class DispatchAgent:
    """
    Interface layer for the Dispatch & Allocation Agent.
    Bridges backend business logic with future LLM/LangGraph/CrewAI framework entries.
    """
    def __init__(self, service: DispatchService = DispatchService()):
        self.service = service
        logger.info("DispatchAgent initialized.")

    async def execute(self, db: Session, task_data: dict) -> dict:
        """
        Executes the agent logic programmatically.
        Expected task_data schema: {"pickup": str, "destination": str, "weight": float}
        """
        logger.info(f"Agent execution triggered with inputs: {task_data}")
        pickup = task_data.get("pickup")
        destination = task_data.get("destination")
        weight = task_data.get("weight")

        if not all([pickup, destination, weight]):
            raise ValueError("Invalid execution inputs. 'pickup', 'destination', and 'weight' are required.")

        return self.service.allocate_dispatch(
            db=db,
            pickup=pickup,
            destination=destination,
            cargo_weight=float(weight)
        )
