from pydantic import BaseModel, Field

class SupervisorRequest(BaseModel):
    workflow: str = Field(..., description="Workflow registry name key (e.g. 'fleet_delivery')")
    pickup: str = Field(..., description="Pickup coordinates or location name")
    destination: str = Field(..., description="Destination coordinates or location name")
    weight: float = Field(..., description="Cargo weight in kilograms")

class SupervisorChatRequest(BaseModel):
    message: str = Field(..., description="Natural language delivery command")

