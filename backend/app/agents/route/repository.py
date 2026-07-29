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
        import uuid
        is_uuid = False
        try:
            uuid.UUID(str(vehicle_id))
            is_uuid = True
        except ValueError:
            pass

        real_uuid = vehicle_id
        if not is_uuid:
            mapping = {
                "v1": "TN38AB1234",
                "v2": "TN38CD5678",
                "v3": "TN38EF9012",
                "v4": "KA-RT-8011",
                "v5": "MH12AB3456",
                "v6": "TN45GH7890"
            }
            lookup_val = mapping.get(vehicle_id, vehicle_id)
            res = db.execute(
                text("SELECT id FROM vehicles WHERE vehicle_number = :lookup_val"),
                {"lookup_val": lookup_val}
            ).first()
            if res:
                real_uuid = str(res[0])
            else:
                return None

        query = text("""
            SELECT vehicle_id, latitude, longitude, speed 
            FROM vehicle_locations 
            WHERE vehicle_id = :vehicle_id
        """)
        try:
            result = db.execute(query, {"vehicle_id": real_uuid}).mappings().first()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching vehicle location: {e}")
            raise e

    @staticmethod
    def get_trip(db: Session, vehicle_id: str) -> dict | None:
        """
        Retrieves the active trip (status in 'Assigned' or 'Pending') assigned to this vehicle.
        """
        import uuid
        is_uuid = False
        try:
            uuid.UUID(str(vehicle_id))
            is_uuid = True
        except ValueError:
            pass

        real_uuid = vehicle_id
        if not is_uuid:
            mapping = {
                "v1": "TN38AB1234",
                "v2": "TN38CD5678",
                "v3": "TN38EF9012",
                "v4": "KA-RT-8011",
                "v5": "MH12AB3456",
                "v6": "TN45GH7890"
            }
            lookup_val = mapping.get(vehicle_id, vehicle_id)
            res = db.execute(
                text("SELECT id FROM vehicles WHERE vehicle_number = :lookup_val"),
                {"lookup_val": lookup_val}
            ).first()
            if res:
                real_uuid = str(res[0])
            else:
                return None

        query = text("""
            SELECT id, vehicle_id, driver_id, source, destination, status 
            FROM trips 
            WHERE vehicle_id = :vehicle_id 
              AND status IN ('Assigned', 'Pending') 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        try:
            result = db.execute(query, {"vehicle_id": real_uuid}).mappings().first()
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
