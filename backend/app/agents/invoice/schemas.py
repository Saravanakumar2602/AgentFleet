from pydantic import BaseModel
class InvoiceRequest(BaseModel):
    trip_id: str
    distance_km: float
    fuel_cost_inr: float
