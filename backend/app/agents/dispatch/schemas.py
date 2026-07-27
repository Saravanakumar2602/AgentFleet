from pydantic import BaseModel, Field

class DispatchRequest(BaseModel):
    pickup: str = Field(..., description="Pickup location name or coordinates (e.g. 'lat,lon')")
    destination: str = Field(..., description="Destination address or coordinates")
    weight: float = Field(..., description="Weight of the cargo in kg", gt=0.0)

class VehicleSummary(BaseModel):
    id: str
    vehicle_number: str

class DriverSummary(BaseModel):
    id: str
    name: str

class DispatchResponse(BaseModel):
    status: str
    agent: str = "Dispatch Agent"
    trip_id: str
    vehicle: VehicleSummary
    driver: DriverSummary
    message: str
