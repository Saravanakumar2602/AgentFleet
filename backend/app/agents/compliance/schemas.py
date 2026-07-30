from pydantic import BaseModel
class ComplianceRequest(BaseModel):
    driver_id: str
    vehicle_id: str
