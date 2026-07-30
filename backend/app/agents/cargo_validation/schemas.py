from pydantic import BaseModel, Field
class CargoValidationRequest(BaseModel):
    pickup: str = Field(..., description="Pickup location")
    destination: str = Field(..., description="Destination location")
    weight: float = Field(..., gt=0, description="Cargo weight in kg")
