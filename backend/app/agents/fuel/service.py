from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger("agentfleet.agents.fuel.service")

FUEL_PRICE_PER_LITER_INR = 102.0   # approximate diesel price ₹/L
FUEL_RESERVE_BUFFER_LITERS = 10.0   # safety reserve


class FuelService:
    """
    Business layer for Fuel Planning Agent.
    Calculates fuel cost and determines if a mid-route refuel stop is needed.
    """

    def plan_fuel(self, db: Session, vehicle_id: str, distance_km: float, estimated_fuel_liters: float) -> dict:
        """
        Evaluates current fuel level against trip requirements and calculates cost.
        """
        logger.info(f"Planning fuel: vehicle={vehicle_id}, distance={distance_km}km, needed={estimated_fuel_liters}L")

        # Fetch current fuel level from DB
        current_fuel_level_pct = 100
        fuel_tank_capacity_liters = 100.0  # default tank size
        try:
            row = db.execute(text("""
                SELECT fuel_level FROM vehicles WHERE id = :vehicle_id
            """), {"vehicle_id": vehicle_id}).first()
            if row and row[0] is not None:
                current_fuel_level_pct = float(row[0])
        except Exception as e:
            logger.warning(f"Could not fetch vehicle fuel level: {e}")

        current_fuel_liters = (current_fuel_level_pct / 100.0) * fuel_tank_capacity_liters
        fuel_after_trip = current_fuel_liters - estimated_fuel_liters

        # Determine if a refuel stop is needed
        refuel_stop_needed = fuel_after_trip < FUEL_RESERVE_BUFFER_LITERS

        # Cost calculation
        estimated_fuel_cost_inr = round(estimated_fuel_liters * FUEL_PRICE_PER_LITER_INR, 2)

        # Refuel stop distance (at 60% of route)
        refuel_stop_km = round(distance_km * 0.6, 1) if refuel_stop_needed else None

        logger.info(
            f"Fuel plan: cost=INR{estimated_fuel_cost_inr}, "
            f"current={current_fuel_liters:.1f}L, after_trip={fuel_after_trip:.1f}L, "
            f"refuel_needed={refuel_stop_needed}"
        )

        return {
            "current_fuel_level_pct": int(current_fuel_level_pct),
            "current_fuel_liters": round(current_fuel_liters, 1),
            "fuel_needed_liters": round(estimated_fuel_liters, 1),
            "fuel_after_trip_liters": round(max(fuel_after_trip, 0), 1),
            "estimated_fuel_cost_inr": estimated_fuel_cost_inr,
            "fuel_price_per_liter": FUEL_PRICE_PER_LITER_INR,
            "refuel_stop_needed": refuel_stop_needed,
            "refuel_stop_km": refuel_stop_km,
        }
