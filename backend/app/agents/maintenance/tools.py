from backend.app.shared.logger import logger

def query_diagnostics_trouble_codes(vehicle_id: str) -> list:
    """
    Simulated tool to retrieve diagnostics codes (DTCs).
    """
    logger.info(f"Checking DTCs for vehicle: {vehicle_id}")
    return ["P0300", "P0171"]
