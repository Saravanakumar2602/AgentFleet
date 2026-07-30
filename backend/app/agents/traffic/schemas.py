from pydantic import BaseModel
class TrafficRequest(BaseModel):
    pickup: str
    destination: str
