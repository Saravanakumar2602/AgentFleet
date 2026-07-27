from sqlalchemy.orm import Session
import logging

from backend.app.agents.analytics.service import AnalyticsService

logger = logging.getLogger("agentfleet.agents.analytics.agent")

class AnalyticsAgent:
    """
    Interface layer for the Fleet Analytics & Optimization Agent.
    Bridges backend business logic with future LLM/LangGraph/CrewAI framework entries.
    """
    def __init__(self, service: AnalyticsService = AnalyticsService()):
        self.service = service
        logger.info("AnalyticsAgent initialized.")

    async def execute(self, db: Session, task_data: dict) -> dict:
        """
        Executes the agent logic programmatically.
        Expected task_data schema: {"vehicle_id": str}
        """
        logger.info(f"Agent execution triggered with inputs: {task_data}")
        vehicle_id = task_data.get("vehicle_id")

        if not vehicle_id:
            raise ValueError("Invalid execution inputs. 'vehicle_id' is required.")

        return self.service.generate_report(
            db=db,
            vehicle_id=vehicle_id
        )
