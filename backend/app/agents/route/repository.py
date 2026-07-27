from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger("agentfleet.agents.route.repository")

class RouteRepository:
    """
    Data Access Object for Route Agent executing raw SQL queries directly.
    """
    @staticmethod
    def get_vehicle_location(db: Session, vehicle_id: str) -> dict | None:
        """
        Fetches the current coordinates of a vehicle from vehicle_locations.
        """
        query = text("""
            SELECT vehicle_id, latitude, longitude, speed 
            FROM vehicle_locations 
            WHERE vehicle_id = :vehicle_id
        """)
        try:
            result = db.execute(query, {"vehicle_id": vehicle_id}).mappings().first()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching vehicle location: {e}")
            raise e

    @staticmethod
    def get_trip(db: Session, vehicle_id: str) -> dict | None:
        """
        Retrieves the active trip (status in 'Assigned' or 'Pending') assigned to this vehicle.
        """
        query = text("""
            SELECT id, vehicle_id, driver_id, source, destination, status 
            FROM trips 
            WHERE vehicle_id = :vehicle_id 
              AND status IN ('Assigned', 'Pending') 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        try:
            result = db.execute(query, {"vehicle_id": vehicle_id}).mappings().first()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching active trip: {e}")
            raise e

    @staticmethod
    def update_trip_route(
        db: Session,
        trip_id: str,
        distance_km: float,
        estimated_duration: int,
        status: str = "Route Generated"
    ) -> None:
        """
        Updates the distance, estimated duration, and operational status of a trip.
        """
        query = text("""
            UPDATE trips 
            SET distance_km = :distance_km, 
                estimated_duration = :estimated_duration, 
                status = :status 
            WHERE id = :trip_id
        """)
        try:
            db.execute(
                query,
                {
                    "distance_km": distance_km,
                    "estimated_duration": estimated_duration,
                    "status": status,
                    "trip_id": trip_id
                }
            )
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating trip route coordinates: {e}")
            raise e
