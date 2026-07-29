import logging
from backend.app.workflows.delivery_workflow import DeliveryWorkflow
from backend.app.workflows.complete_trip_workflow import CompleteTripWorkflow

logger = logging.getLogger("agentfleet.workflows.registry")

# Global Workflow Registry mapping name keys to workflow instances
WORKFLOW_REGISTRY = {
    "fleet_delivery": DeliveryWorkflow(),
    "complete_trip": CompleteTripWorkflow()
}

def get_workflow(name: str):
    """
    Retrieves the workflow instance associated with the registered name.
    Returns None if the name is not registered.
    """
    logger.info(f"Retrieving workflow: '{name}'")
    return WORKFLOW_REGISTRY.get(name.lower().strip())
