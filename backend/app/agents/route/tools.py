from backend.app.shared.logger import logger

def query_traffic_delay_multiplier(route_id: str) -> float:
    """
    Simulated tool to fetch traffic delay indexes.
    """
    logger.info(f"Checking delay index for route: {route_id}")
    return 1.15
