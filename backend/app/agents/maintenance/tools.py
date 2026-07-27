from backend.app.shared.logger import logger

def fetch_vehicle_service_history(vehicle_id: str) -> list:
    """
    Simulated tool to query database for past maintenance history of a vehicle.
    """
    logger.info(f"Fetching service records for vehicle: {vehicle_id}")
    return [
        {"date": "2026-05-12", "type": "Oil Change", "mileage": 85000.0},
        {"date": "2026-02-18", "type": "Brake Pad Replacement", "mileage": 78200.0}
    ]
