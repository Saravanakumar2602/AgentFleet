from backend.app.shared.exceptions import InvalidCoordinateException

def validate_coordinates(lat: float, lon: float, raise_on_error: bool = False) -> bool:
    """
    Validates physical coordinate ranges:
    Latitude: [-90, 90], Longitude: [-180, 180]
    """
    is_valid = -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
    if not is_valid and raise_on_error:
        raise InvalidCoordinateException(f"Invalid coordinate bounds: lat={lat}, lon={lon}")
    return is_valid

def parse_coordinates(location_str: str) -> tuple[float, float] | None:
    """
    Parses 'latitude,longitude' format.
    Returns (lat, lon) tuple, or None if parsing/validation fails.
    """
    try:
        parts = location_str.split(",")
        if len(parts) == 2:
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            if validate_coordinates(lat, lon):
                return lat, lon
    except Exception:
        pass
    return None
