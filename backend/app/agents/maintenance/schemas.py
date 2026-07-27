from pydantic import BaseModel, Field
from typing import Optional

class MaintenanceRequest(BaseModel):
    vehicle_id: str = Field(..., description="Unique vehicle UUID string")

class MaintenanceResponse(BaseModel):
    status: str
    agent: str = "Maintenance Agent"
    vehicle_id: Optional[str] = Field(None, description="Vehicle ID associated with response")
    health_score: float = Field(..., description="Vehicle diagnostic health rating (0-100)")
    vehicle_status: str = Field(..., description="Diagnostic state ('Healthy', 'Service Recommended', 'Maintenance Required')")
    next_service_after_km: Optional[int] = Field(None, description="Distance remaining until next inspection is scheduled")
    message: str = Field(..., description="Details regarding vehicle health assessment")
