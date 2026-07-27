from fastapi import APIRouter
from app.schemas import DispatchRequest
from app.service import DispatchService
from app.mock_data import VEHICLES, DRIVERS

router = APIRouter()

@router.post("/dispatch")
def match_delivery_dispatch(payload: DispatchRequest):
    """
    Exposes POST /dispatch API.
    Resolves matching vehicle and driver.
    """
    return DispatchService.match_dispatch(
        pickup=payload.pickup,
        destination=payload.destination,
        weight=payload.weight
    )

@router.get("/fleet")
def get_fleet_status():
    """
    Helper API returning the current status of vehicles and drivers.
    """
    return {
        "vehicles": VEHICLES,
        "drivers": DRIVERS
    }
