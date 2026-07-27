from pydantic import BaseModel, Field

class NotificationRequest(BaseModel):
    trip_id: str = Field(..., description="Trip UUID identifier")

class NotificationResponse(BaseModel):
    status: str
    agent: str = "Customer Agent"
    trip_id: str = Field(..., description="Trip UUID identifier")
    customer_message: str = Field(..., description="Formatted tracking message")
    notification_type: str = Field("Trip Update", description="Classification of the alert event")
