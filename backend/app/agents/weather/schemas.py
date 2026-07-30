from pydantic import BaseModel
class WeatherRequest(BaseModel):
    destination: str
