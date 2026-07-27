from pydantic import BaseModel, Field
from typing import Optional

class DispatchRequest(BaseModel):
    pickup_location: str = Field(..., description="Starting location coordinates or address")
    destination: str = Field(..., description="Target destination coordinates or address")
    load_weight: float = Field(..., description="Weight of the load in kilograms", gt=0)
    special_requirements: Optional[str] = Field(None, description="E.g. cold chain, hazardous materials")

class DispatchResponseSchema(BaseModel):
    assigned_vehicle_id: str
    driver_id: str
    load_weight: float
    destination: str
