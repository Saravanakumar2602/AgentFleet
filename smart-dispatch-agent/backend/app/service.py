import random
from app.mock_data import VEHICLES, DRIVERS

class DispatchService:
    """
    Business layer matching available vehicles and drivers.
    """
    @staticmethod
    def match_dispatch(pickup: str, destination: str, weight: float) -> dict:
        # 1. Choose matching vehicle: status == Available, capacity >= weight
        matched_vehicle = None
        for v in VEHICLES:
            if v["status"] == "Available" and v["capacity"] >= weight:
                # We can choose the first matching or best matching. First matching is requested.
                matched_vehicle = v
                break

        # 2. Choose first matching driver: status == Available
        matched_driver = None
        for d in DRIVERS:
            if d["status"] == "Available":
                matched_driver = d
                break

        # 3. If either matching vehicle or driver is not found
        if not matched_vehicle or not matched_driver:
            return {
                "status": "failed",
                "message": "No suitable vehicle available."
            }

        # 4. Generate random hours between 4 and 9
        estimated_hours = random.randint(4, 9)

        # 5. Return success payload
        return {
            "status": "success",
            "vehicle_number": matched_vehicle["vehicle_number"],
            "capacity": matched_vehicle["capacity"],
            "driver": matched_driver["name"],
            "pickup": pickup,
            "destination": destination,
            "estimated_time": f"{estimated_hours} Hours",
            "message": "Vehicle Assigned Successfully"
        }
