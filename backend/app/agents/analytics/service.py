from sqlalchemy.orm import Session
import logging

from backend.app.agents.analytics.repository import AnalyticsRepository
from backend.app.shared.exceptions import VehicleUnavailableException

logger = logging.getLogger("agentfleet.agents.analytics.service")

class AnalyticsService:
    """
    Business layer for Fleet Analytics & Optimization Agent.
    Aggregates metrics and triggers rule recommendations.
    """
    def __init__(self, repository: AnalyticsRepository = AnalyticsRepository()):
        self.repository = repository

    def generate_report(self, db: Session, vehicle_id: str) -> dict:
        """
        Retrieves statistics for a vehicle, computes efficiency and utilization,
        evaluates performance rules, and builds the analytics report.
        """
        logger.info(f"Generating analytics report: vehicle={vehicle_id}")

        # 1. Fetch vehicle
        vehicle = self.repository.get_vehicle(db, vehicle_id)
        if not vehicle:
            logger.warning(f"Vehicle not found in database: {vehicle_id}")
            raise VehicleUnavailableException("Vehicle not found.")

        # 2. Retrieve statistics
        trip_stats = self.repository.get_trip_statistics(db, vehicle_id)
        maintenance_count = self.repository.get_maintenance_statistics(db, vehicle_id)
        fleet_avg_efficiency = self.repository.get_fleet_average_fuel_efficiency(db)

        # 3. Compute calculations
        total_trips = int(trip_stats["total_trips"])
        average_distance = round(float(trip_stats["avg_distance"]), 1)
        total_distance = float(trip_stats["total_distance"])
        total_fuel = float(trip_stats["total_fuel"])

        # Fuel efficiency (km/L)
        fuel_efficiency = 0.0
        if total_fuel > 0.0:
            fuel_efficiency = round(total_distance / total_fuel, 1)

        # Utilization % (target 17,000 km represents 100% utilization)
        utilization = 0
        if total_distance > 0.0:
            utilization = min(int((total_distance / 17000.0) * 100), 100)

        # 4. Evaluate Recommendation Rules
        # Default baseline fleet average is 8.0 km/L if no database logs exist
        fleet_avg = fleet_avg_efficiency if fleet_avg_efficiency > 0.0 else 8.0

        if utilization < 40:
            recommendation = "Vehicle underutilized."
        elif maintenance_count > 5:
            recommendation = "Frequent maintenance detected."
        elif fuel_efficiency < fleet_avg and fuel_efficiency > 0.0:
            recommendation = "Vehicle fuel efficiency is below fleet average."
        else:
            recommendation = "Vehicle operating normally."

        logger.info(f"Report generated successfully: trips={total_trips}, utilization={utilization}%, recommendation='{recommendation}'")

        return {
            "vehicle": vehicle["vehicle_number"],
            "total_trips": total_trips,
            "average_distance": average_distance,
            "fuel_efficiency": fuel_efficiency,
            "maintenance_count": maintenance_count,
            "utilization": utilization,
            "recommendation": recommendation
        }
