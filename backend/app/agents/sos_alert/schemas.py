from pydantic import BaseModel
class SosAlertRequest(BaseModel):
    weather_risk: str = "Low"
    health_score: int = 100
    vehicle_id: str = ""
    trip_id: str = ""
