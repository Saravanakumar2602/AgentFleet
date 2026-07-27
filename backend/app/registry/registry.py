import logging

# Import concrete agent definitions
from backend.app.agents.dispatch.agent import DispatchAgent
from backend.app.agents.route.agent import RouteAgent
from backend.app.agents.maintenance.agent import MaintenanceAgent
from backend.app.agents.analytics.agent import AnalyticsAgent

logger = logging.getLogger("agentfleet.registry")

# Global Registry mapping name keys to agent singleton instances
AGENT_REGISTRY = {
    "dispatch": DispatchAgent(),
    "route": RouteAgent(),
    "maintenance": MaintenanceAgent(),
    "analytics": AnalyticsAgent()
}

def get_agent(name: str):
    """
    Retrieves the concrete agent instance associated with the registered name.
    Returns None if the name is not registered.
    """
    logger.info(f"Retrieving agent from registry: '{name}'")
    return AGENT_REGISTRY.get(name.lower().strip())
