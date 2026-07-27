from pydantic import BaseModel, Field

class DeliveryWorkflowRequest(BaseModel):
    pickup: str = Field(..., description="Coordinates of pickup location (e.g. '12.9715,77.5945')")
    destination: str = Field(..., description="Coordinates of destination location (e.g. '12.9820,77.6010')")
    weight: float = Field(..., description="Cargo weight in kilograms")
