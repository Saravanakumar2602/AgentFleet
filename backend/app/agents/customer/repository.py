from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger("agentfleet.agents.customer.repository")

class CustomerRepository:
    """
    Data Access Object for Customer Communication Agent executing direct SQL queries.
    """
    @staticmethod
    def get_trip(db: Session, trip_id: str) -> dict | None:
        """
        Retrieves a trip by ID.
        """
        query = text("""
            SELECT id, vehicle_id, driver_id, source, destination, distance_km, estimated_duration, status 
            FROM trips 
            WHERE id = :trip_id
        """)
        try:
            result = db.execute(query, {"trip_id": trip_id}).mappings().first()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching trip details: {e}")
            raise e

    @staticmethod
    def get_vehicle(db: Session, vehicle_id: str) -> dict | None:
        """
        Retrieves a vehicle by ID.
        """
        query = text("""
            SELECT id, vehicle_number, vehicle_type 
            FROM vehicles 
            WHERE id = :vehicle_id
        """)
        try:
            result = db.execute(query, {"vehicle_id": vehicle_id}).mappings().first()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching vehicle details: {e}")
            raise e

    @staticmethod
    def get_driver(db: Session, driver_id: str) -> dict | None:
        """
        Retrieves driver user profile details by driver ID.
        """
        query = text("""
            SELECT d.id, d.user_id, u.name, d.phone 
            FROM drivers d 
            JOIN users u ON d.user_id = u.id 
            WHERE d.id = :driver_id
        """)
        try:
            result = db.execute(query, {"driver_id": driver_id}).mappings().first()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching driver user details: {e}")
            raise e

    @staticmethod
    def insert_notification(
        db: Session, 
        trip_id: str, 
        message: str, 
        notification_type: str = "Dispatch_Notice"
    ) -> str:
        import uuid
        notif_uuid = str(uuid.uuid4())
        query = text("""
            INSERT INTO notifications (id, trip_id, message, notification_type, status, sent_at)
            VALUES (:id, :trip_id, :message, :notification_type, 'Sent', NOW())
        """)
        try:
            db.execute(
                query,
                {
                    "id": notif_uuid,
                    "trip_id": trip_id,
                    "message": message,
                    "notification_type": notification_type
                }
            )
            db.commit()
            return notif_uuid
        except Exception as e:
            db.rollback()
            logger.error(f"Error inserting customer notification: {e}")
            raise e
