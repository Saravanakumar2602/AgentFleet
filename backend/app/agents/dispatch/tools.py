from backend.app.shared.logger import logger

def query_available_fleet_vehicles(max_distance_km: float) -> list:
    """
    Simulated tool to query database for vehicles within a search radius.
    """
    logger.info(f"Querying vehicles within {max_distance_km} km radius.")
    # Return placeholder fleet data
    return [
        {"vehicle_id": "VEH-TEMP-01", "type": "Dry Van", "distance": 12.5},
        {"vehicle_id": "VEH-TEMP-02", "type": "Reefer", "distance": 24.1}
    ]
