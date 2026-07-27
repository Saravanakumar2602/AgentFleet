from backend.app.shared.logger import logger

def query_historical_fuel_logs(vehicle_class: str, days: int) -> list:
    """
    Simulated tool to query historical database tables for fuel and mileage entries.
    """
    logger.info(f"Retrieving fuel logs for class '{vehicle_class}' over last {days} days.")
    return [
        {"log_id": 100, "vehicle_id": "V-1", "liters": 150.0, "distance_km": 450.0},
        {"log_id": 101, "vehicle_id": "V-2", "liters": 180.0, "distance_km": 510.0}
    ]
