from pydantic import BaseModel
class EtaUpdaterRequest(BaseModel):
    base_duration_minutes: int
    traffic_delay_minutes: int = 0
    weather_delay_minutes: int = 0
