from pydantic import BaseModel
class FuelRequest(BaseModel):
    vehicle_id: str
    distance_km: float
    estimated_fuel_liters: float
