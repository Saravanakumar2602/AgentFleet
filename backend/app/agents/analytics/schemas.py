from pydantic import BaseModel, Field

class AnalyticsRequest(BaseModel):
    vehicle_id: str = Field(..., description="Vehicle UUID identifier")

class AnalyticsResponse(BaseModel):
    status: str
    agent: str = "Fleet Analytics Agent"
    vehicle: str = Field(..., description="Vehicle registration number")
    total_trips: int = Field(..., description="Total completed trips count")
    average_distance: float = Field(..., description="Average travel distance in kilometers")
    fuel_efficiency: float = Field(..., description="Computed vehicle fuel efficiency in km/L")
    maintenance_count: int = Field(..., description="Total count of recorded maintenance events")
    utilization: int = Field(..., description="Calculated vehicle utilization percentage (0-100)")
    recommendation: str = Field(..., description="Rule-based operations recommendation suggestion")
