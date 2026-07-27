from pydantic import BaseModel, Field

class RouteRequest(BaseModel):
    vehicle_id: str = Field(..., description="Vehicle UUID identifier")
    pickup: str = Field(..., description="Coordinates of the pickup location (e.g., '13.0827,80.2707')")
    destination: str = Field(..., description="Coordinates of the destination location (e.g., '11.0168,76.9558')")

class RouteResponse(BaseModel):
    status: str
    agent: str = "Route Agent"
    trip_id: str
    distance_km: float
    estimated_duration: str
    estimated_fuel: float
    message: str
