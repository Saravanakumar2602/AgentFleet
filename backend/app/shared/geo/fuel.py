def estimate_fuel(distance_km: float, fuel_rate_l_100km: float = 12.0) -> float:
    """
    Estimates fuel consumption in liters.
    Default fuel consumption rate is 12L per 100km.
    """
    if distance_km <= 0.0 or fuel_rate_l_100km <= 0.0:
        return 0.0
    return round((distance_km * fuel_rate_l_100km) / 100.0, 2)
