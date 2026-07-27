from pydantic import BaseModel, Field
from typing import Optional

class AnalyticsReportRequest(BaseModel):
    days_range: int = Field(30, description="Time window for report analysis in days", gt=0)
    vehicle_class: Optional[str] = Field(None, description="Filter for specific category (e.g. heavy-duty, light-truck)")

class AnalyticsResponseSchema(BaseModel):
    days_range: int
    fleet_utilization_rate: float
    total_trips_completed: int
    deadhead_miles_percentage: float
    cost_savings_estimate_usd: float
