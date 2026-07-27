from enum import Enum

class FleetIntent(str, Enum):
    """
    Enum representing structural operational actions classified by the system.
    """
    DISPATCH = "dispatch"
    ROUTE = "route"
    MAINTENANCE = "maintenance"
    ANALYTICS = "analytics"
    CUSTOMER = "customer"
    WORKFLOW = "workflow"
    UNKNOWN = "unknown"
