from pydantic import BaseModel, Field

class DispatchRequest(BaseModel):
    pickup: str = Field(..., min_length=1, description="Pickup location name")
    destination: str = Field(..., min_length=1, description="Destination location name")
    weight: float = Field(..., gt=0, description="Cargo weight in kg")
