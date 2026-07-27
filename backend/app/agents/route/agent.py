from sqlalchemy.orm import Session
import logging

from backend.app.agents.route.service import RouteService

logger = logging.getLogger("agentfleet.agents.route.agent")

class RouteAgent:
    """
    Interface layer for the Route Intelligence Agent.
    Bridges backend business logic with future LLM/LangGraph/CrewAI framework entries.
    """
    def __init__(self, service: RouteService = RouteService()):
        self.service = service
        logger.info("RouteAgent initialized.")

    async def execute(self, db: Session, task_data: dict) -> dict:
        """
        Executes the agent logic programmatically.
        Expected task_data schema: {"vehicle_id": str, "pickup": str, "destination": str}
        """
        logger.info(f"Agent execution triggered with inputs: {task_data}")
        vehicle_id = task_data.get("vehicle_id")
        pickup = task_data.get("pickup")
        destination = task_data.get("destination")

        if not all([vehicle_id, pickup, destination]):
            raise ValueError("Invalid execution inputs. 'vehicle_id', 'pickup', and 'destination' are required.")

        return self.service.generate_route(
            db=db,
            vehicle_id=vehicle_id,
            pickup=pickup,
            destination=destination
        )
