from pydantic import BaseModel, Field
from typing import List, Optional

class RouteOptimizationRequest(BaseModel):
    origin: str = Field(..., description="Starting location coordinate or address")
    destination: str = Field(..., description="Target destination coordinate or address")
    avoid_tolls: bool = Field(False, description="Flag to indicate whether toll routes should be avoided")
    traffic_avoidance_level: Optional[str] = Field("standard", description="Avoidance weight: low, standard, high")

class RouteResponseSchema(BaseModel):
    origin: str
    destination: str
    waypoints: List[str]
    distance_km: float
    duration_minutes: int
