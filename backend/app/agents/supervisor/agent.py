from sqlalchemy.orm import Session
import logging

from backend.app.agents.supervisor.service import SupervisorService

logger = logging.getLogger("agentfleet.agents.supervisor.agent")

class SupervisorAgent:
    """
    Interface layer for the Fleet Supervisor Agent.
    Orchestrates high-level multi-agent workflows.
    """
    def __init__(self, service: SupervisorService = SupervisorService()):
        self.service = service
        logger.info("SupervisorAgent initialized.")

    def execute(self, db: Session, task_data: dict) -> dict:
        """
        Executes workflow orchestration programmatically.
        Expected task_data schema: {"workflow": str, "pickup": str, "destination": str, "weight": float}
        """
        logger.info(f"SupervisorAgent triggered execution: {task_data}")
        workflow = task_data.get("workflow")
        pickup = task_data.get("pickup")
        destination = task_data.get("destination")
        weight = task_data.get("weight")

        if not all([workflow, pickup, destination, weight]):
            raise ValueError("Invalid execution inputs. 'workflow', 'pickup', 'destination', and 'weight' are required.")

        return self.service.execute_workflow(
            db=db,
            workflow_name=workflow,
            pickup=pickup,
            destination=destination,
            weight=float(weight)
        )
