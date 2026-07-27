from pydantic import BaseModel, Field
from typing import Dict, Any

class TelemetryReportRequest(BaseModel):
    vehicle_id: str = Field(..., description="Unique vehicle identifier string")
    mileage_km: float = Field(..., description="Current odometer mileage in km", ge=0)
    telemetry_data: Dict[str, Any] = Field(
        ..., 
        description="Key-value pairs of diagnostic stats (e.g. engine_temperature_c, tire_pressure_psi)"
    )

class TelemetryResponseSchema(BaseModel):
    vehicle_id: str
    evaluation_status: str
    recommendation: str
