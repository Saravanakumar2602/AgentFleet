from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger("agentfleet.agents.dispatch.repository")

class DispatchRepository:
    """
    Data Access Object for Dispatch Agent executing SQL queries directly.
    """
    @staticmethod
    def get_available_vehicles(db: Session) -> list:
        """
        Retrieves all vehicles with status 'Available' joined with location coordinates.
        """
        query = text("""
            SELECT v.id, v.vehicle_number, v.capacity_kg, vl.latitude, vl.longitude 
            FROM vehicles v
            LEFT JOIN vehicle_locations vl ON v.id = vl.vehicle_id
            WHERE v.status = 'Available'
        """)
        try:
            result = db.execute(query)
            # Map Row objects to dicts
            return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error fetching available vehicles: {e}")
            raise e

    @staticmethod
    def get_available_drivers(db: Session) -> list:
        """
        Retrieves all drivers with status 'Available' joined with user names.
        """
        query = text("""
            SELECT d.id, u.name 
            FROM drivers d
            JOIN users u ON d.user_id = u.id
            WHERE d.status = 'Available'
        """)
        try:
            result = db.execute(query)
            return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error fetching available drivers: {e}")
            raise e

    @staticmethod
    def create_trip(
        db: Session,
        vehicle_id: str,
        driver_id: str,
        source: str,
        destination: str,
        distance_km: float,
        estimated_duration: int
    ) -> str:
        """
        Registers a new trip in the database and returns the generated trip UUID string.
        """
        import uuid
        trip_uuid = str(uuid.uuid4())
        query = text("""
            INSERT INTO trips (id, vehicle_id, driver_id, source, destination, distance_km, estimated_duration, status, created_at)
            VALUES (:id, :vehicle_id, :driver_id, :source, :destination, :distance_km, :estimated_duration, 'Assigned', NOW())
        """)
        try:
            db.execute(
                query,
                {
                    "id": trip_uuid,
                    "vehicle_id": vehicle_id,
                    "driver_id": driver_id,
                    "source": source,
                    "destination": destination,
                    "distance_km": distance_km,
                    "estimated_duration": estimated_duration
                }
            )
            db.commit()
            return trip_uuid
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating trip: {e}")
            raise e

    @staticmethod
    def update_vehicle_status(db: Session, vehicle_id: str, status: str) -> None:
        """
        Updates the operational status of a vehicle.
        """
        query = text("""
            UPDATE vehicles 
            SET status = :status 
            WHERE id = :vehicle_id
        """)
        try:
            db.execute(query, {"status": status, "vehicle_id": vehicle_id})
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating vehicle status to '{status}': {e}")
            raise e

    @staticmethod
    def update_driver_status(db: Session, driver_id: str, status: str) -> None:
        """
        Updates the operational status of a driver.
        """
        query = text("""
            UPDATE drivers 
            SET status = :status 
            WHERE id = :driver_id
        """)
        try:
            db.execute(query, {"status": status, "driver_id": driver_id})
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating driver status to '{status}': {e}")
            raise e
