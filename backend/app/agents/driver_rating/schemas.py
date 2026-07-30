from pydantic import BaseModel
class DriverRatingRequest(BaseModel):
    driver_id: str
