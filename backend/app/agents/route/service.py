from sqlalchemy.orm import Session
import logging

from backend.app.agents.route.repository import RouteRepository
from backend.app.shared.exceptions import InvalidCoordinateException, VehicleUnavailableException, AgentFleetException
from backend.app.shared.geo.coordinates import parse_coordinates
from backend.app.shared.geo.distance import haversine_distance
from backend.app.shared.geo.eta import estimate_eta
from backend.app.shared.geo.fuel import estimate_fuel

from backend.app.core.config import settings

logger = logging.getLogger("agentfleet.agents.route.service")

class RouteService:
    """
    Business layer for Route Intelligence Agent.
    Coordinates route calculations and database transitions using shared helper utilities.
    """
    def __init__(self, repository: RouteRepository = RouteRepository()):
        self.repository = repository

    def generate_route(self, db: Session, vehicle_id: str, pickup: str, destination: str) -> dict:
        """
        Validates pickup/destination coordinates, verifies vehicle coordinates,
        calculates metrics, and updates active trip.
        """
        logger.info(f"Generating route metrics: vehicle={vehicle_id}, pickup='{pickup}', destination='{destination}'")

        # 1. Parse and validate pickup and destination coordinates
        pickup_coords = parse_coordinates(pickup)
        dest_coords = parse_coordinates(destination)

        if not pickup_coords or not dest_coords:
            logger.warning("Route generation failed: Invalid coordinate parameters.")
            raise InvalidCoordinateException("Invalid coordinates.")

        # 2. Verify that the vehicle location registry exists in the database
        vehicle_loc = self.repository.get_vehicle_location(db, vehicle_id)
        if not vehicle_loc:
            logger.warning(f"Route generation failed: Vehicle location registry not found for ID: {vehicle_id}")
            raise VehicleUnavailableException("Vehicle not found.")

        # 3. Retrieve the active trip currently assigned to this vehicle
        trip = self.repository.get_trip(db, vehicle_id)
        if not trip:
            logger.warning(f"Route generation failed: No active Assigned/Pending trip found for vehicle: {vehicle_id}")
            raise AgentFleetException("No active trip found for this vehicle.")

        # 4. Calculate Haversine distance
        p_lat, p_lon = pickup_coords
        d_lat, d_lon = dest_coords
        distance_km = haversine_distance(p_lat, p_lon, d_lat, d_lon)
        if distance_km <= 0.0:
            distance_km = 1.0

        # 5. Estimate duration (Use speed from configuration)
        minutes = estimate_eta(distance_km, speed_kmh=settings.ROUTE_DEFAULT_SPEED_KMH)
        hours = minutes // 60
        mins = minutes % 60
        duration_str = f"{hours}h {mins}m"

        # 6. Estimate fuel consumption (Using baseline consumption rate from configuration)
        fuel_liters = estimate_fuel(distance_km, fuel_rate_l_100km=settings.ROUTE_FUEL_L_PER_100KM)

        # 7. Update database record
        try:
            self.repository.update_trip_route(
                db=db,
                trip_id=trip["id"],
                distance_km=distance_km,
                estimated_duration=minutes,
                status="Route Generated"
            )
            logger.info(f"Trip {trip['id']} successfully updated with status 'Route Generated'.")
        except Exception as e:
            logger.error(f"Failed to commit trip route updates: {e}")
            raise e

        return {
            "trip_id": str(trip["id"]),
            "distance_km": round(distance_km, 1),
            "estimated_duration": duration_str,
            "estimated_fuel": round(fuel_liters, 1)
        }
