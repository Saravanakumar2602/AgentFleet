from pydantic import BaseModel, Field

class SupervisorEscalationRequest(BaseModel):
    incident_id: str = Field(..., description="Unique incident identifier")
    incident_description: str = Field(..., description="Detailed explanation of the agent conflict or event")
    failed_agent: str = Field(..., description="The name of the agent encountering issues")

class SupervisorResponseSchema(BaseModel):
    incident_id: str
    orchestrated_action: str
    status: str
