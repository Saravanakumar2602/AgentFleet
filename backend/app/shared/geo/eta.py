def estimate_eta(distance_km: float, speed_kmh: float = 45.0) -> int:
    """
    Estimates travel time in minutes based on distance and average speed.
    Guarantees a minimum value of 5 minutes.
    """
    if distance_km <= 0.0 or speed_kmh <= 0.0:
        return 5
    return max(int((distance_km / speed_kmh) * 60.0), 5)
