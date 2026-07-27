from pydantic import BaseModel, Field

class NotificationTriggerRequest(BaseModel):
    customer_contact: str = Field(..., description="Email address or phone number of the target client")
    notification_channel: str = Field("email", description="Channel choice: email, sms, WhatsApp")
    trip_id: str = Field(..., description="The corresponding trip UUID string")

class NotificationResponseSchema(BaseModel):
    customer_contact: str
    channel_used: str
    message_sent: str
    dispatch_status: str
