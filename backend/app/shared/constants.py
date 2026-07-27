from enum import Enum

class AgentName(str, Enum):
    DISPATCH = "dispatch"
    ROUTE = "route"
    MAINTENANCE = "maintenance"
    ANALYTICS = "analytics"
    CUSTOMER = "customer"
    SUPERVISOR = "supervisor"

class DispatchStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class VehicleStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
