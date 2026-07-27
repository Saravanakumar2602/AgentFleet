from sqlalchemy.orm import Session
import logging

from backend.app.agents.dispatch.repository import DispatchRepository
from backend.app.shared.exceptions import DriverUnavailableException, VehicleUnavailableException
from backend.app.shared.geo.coordinates import parse_coordinates
from backend.app.shared.geo.distance import haversine_distance
from backend.app.shared.geo.eta import estimate_eta

logger = logging.getLogger("agentfleet.agents.dispatch.service")

class DispatchService:
    """
    Business layer for Dispatch & Allocation Agent.
    Coordinates rules, filters, and status transitions using shared helper utilities.
    """
    def __init__(self, repository: DispatchRepository = DispatchRepository()):
        self.repository = repository

    def allocate_dispatch(self, db: Session, pickup: str, destination: str, cargo_weight: float) -> dict:
        """
        Calculates driver and vehicle matches, sets statuses to busy, and registers trip.
        Uses shared geocode parsing, Haversine routing math, and custom exceptions.
        """
        logger.info(f"Calculating dispatch match: weight={cargo_weight} kg, pickup='{pickup}', destination='{destination}'")

        # 1. Fetch available drivers
        drivers = self.repository.get_available_drivers(db)
        if not drivers:
            logger.warning("Dispatch allocation failed: No available drivers found.")
            raise DriverUnavailableException("No available drivers found.")

        # 2. Fetch available vehicles
        vehicles = self.repository.get_available_vehicles(db)
        if not vehicles:
            logger.warning("Dispatch allocation failed: No available vehicles found.")
            raise VehicleUnavailableException("No available vehicles found.")

        # 3. Filter vehicles by capacity (capacity_kg >= cargo_weight)
        suitable_vehicles = [
            v for v in vehicles 
            if v["capacity_kg"] is not None and float(v["capacity_kg"]) >= cargo_weight
        ]

        if not suitable_vehicles:
            logger.warning(f"Dispatch allocation failed: No suitable vehicle of capacity >= {cargo_weight} kg found.")
            raise VehicleUnavailableException("No suitable vehicle found.")

        # 4. Choose vehicle: nearest vehicle if coordinates parsed, otherwise first matching vehicle
        assigned_vehicle = None
        pickup_coords = parse_coordinates(pickup)

        if pickup_coords:
            p_lat, p_lon = pickup_coords
            best_dist = float("inf")
            for v in suitable_vehicles:
                if v.get("latitude") is not None and v.get("longitude") is not None:
                    # Calculate using shared Haversine distance formula
                    dist = haversine_distance(p_lat, p_lon, float(v["latitude"]), float(v["longitude"]))
                    if dist < best_dist:
                        best_dist = dist
                        assigned_vehicle = v
            if assigned_vehicle:
                logger.info(f"Assigned nearest vehicle: {assigned_vehicle['vehicle_number']} (distance: {best_dist:.2f} km)")

        # Fallback to first matched vehicle if coordinates matching failed or was not possible
        if not assigned_vehicle:
            assigned_vehicle = suitable_vehicles[0]
            logger.info(f"Using default assignment. Selected vehicle: {assigned_vehicle['vehicle_number']}")

        # 5. Assign the first available driver
        assigned_driver = drivers[0]
        logger.info(f"Assigned driver: {assigned_driver['name']} to vehicle {assigned_vehicle['vehicle_number']}")

        # 6. Determine metrics using shared modules
        distance_km = 20.0
        dest_coords = parse_coordinates(destination)
        if pickup_coords and dest_coords:
            p_lat, p_lon = pickup_coords
            d_lat, d_lon = dest_coords
            distance_km = haversine_distance(p_lat, p_lon, d_lat, d_lon)
            if distance_km <= 0.0:
                distance_km = 1.0

        # Estimate duration using shared ETA module
        estimated_duration = estimate_eta(distance_km, speed_kmh=45.0)

        # 7. Create database records in a safe transaction block
        try:
            trip_id = self.repository.create_trip(
                db=db,
                vehicle_id=assigned_vehicle["id"],
                driver_id=assigned_driver["id"],
                source=pickup,
                destination=destination,
                distance_km=distance_km,
                estimated_duration=estimated_duration
            )

            # Update database status columns
            self.repository.update_vehicle_status(db, assigned_vehicle["id"], "Busy")
            self.repository.update_driver_status(db, assigned_driver["id"], "Busy")
            logger.info(f"Trip successfully registered with ID: {trip_id}. Statuses updated to 'Busy'.")
        except Exception as e:
            logger.error(f"Failed to execute database transactions for trip matching: {e}")
            raise e

        return {
            "trip_id": trip_id,
            "vehicle": {
                "id": str(assigned_vehicle["id"]),
                "vehicle_number": assigned_vehicle["vehicle_number"]
            },
            "driver": {
                "id": str(assigned_driver["id"]),
                "name": assigned_driver["name"]
            }
        }
