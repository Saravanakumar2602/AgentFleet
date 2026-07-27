from backend.app.shared.logger import logger

def query_traffic_conditions(route_segment: str) -> dict:
    """
    Simulated tool to query real-time traffic API for a specific route segment.
    """
    logger.info(f"Querying traffic conditions for segment: {route_segment}")
    return {"segment": route_segment, "congestion_index": 0.2, "delay_seconds": 120}

def query_weather_forecast(lat: float, lon: float) -> dict:
    """
    Simulated tool to query weather API for coordinates.
    """
    logger.info(f"Querying weather for coordinates: {lat}, {lon}")
    return {"lat": lat, "lon": lon, "condition": "Clear", "alert": None}
