import logging

# Import all 15 agent definitions
from backend.app.agents.cargo_validation.agent import CargoValidationAgent
from backend.app.agents.dispatch.agent import DispatchAgent
from backend.app.agents.traffic.agent import TrafficAgent
from backend.app.agents.weather.agent import WeatherAgent
from backend.app.agents.route.agent import RouteAgent
from backend.app.agents.eta_updater.agent import EtaUpdaterAgent
from backend.app.agents.compliance.agent import ComplianceAgent
from backend.app.agents.maintenance.agent import MaintenanceAgent
from backend.app.agents.fuel.agent import FuelAgent
from backend.app.agents.analytics.agent import AnalyticsAgent
from backend.app.agents.driver_rating.agent import DriverRatingAgent
from backend.app.agents.customer.agent import CustomerAgent
from backend.app.agents.invoice.agent import InvoiceAgent
from backend.app.agents.fleet_summary.agent import FleetSummaryAgent
from backend.app.agents.sos_alert.agent import SosAlertAgent

logger = logging.getLogger("agentfleet.registry")

# Global Registry mapping name keys to agent singleton instances
AGENT_REGISTRY = {
    "cargo_validation": CargoValidationAgent(),
    "dispatch":         DispatchAgent(),
    "traffic":          TrafficAgent(),
    "weather":          WeatherAgent(),
    "route":            RouteAgent(),
    "eta_updater":      EtaUpdaterAgent(),
    "compliance":       ComplianceAgent(),
    "maintenance":      MaintenanceAgent(),
    "fuel":             FuelAgent(),
    "analytics":        AnalyticsAgent(),
    "driver_rating":    DriverRatingAgent(),
    "customer":         CustomerAgent(),
    "invoice":          InvoiceAgent(),
    "fleet_summary":    FleetSummaryAgent(),
    "sos_alert":        SosAlertAgent(),
}

def get_agent(name: str):
    """
    Retrieves the concrete agent instance associated with the registered name.
    Returns None if the name is not registered.
    """
    logger.info(f"Retrieving agent from registry: '{name}'")
    return AGENT_REGISTRY.get(name.lower().strip())
