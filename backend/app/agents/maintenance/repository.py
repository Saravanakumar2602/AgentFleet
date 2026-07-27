from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger("agentfleet.agents.maintenance.repository")

class MaintenanceRepository:
    """
    Data Access Object for Maintenance Agent executing raw SQL queries directly.
    """
    @staticmethod
    def get_vehicle(db: Session, vehicle_id: str) -> dict | None:
        """
        Fetches vehicle record by ID.
        """
        query = text("""
            SELECT id, vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score 
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
    def get_latest_maintenance(db: Session, vehicle_id: str) -> dict | None:
        """
        Fetches the single latest maintenance log entry for a vehicle.
        """
        query = text("""
            SELECT id, vehicle_id, issue, health_score, service_date, next_service_date, status 
            FROM maintenance_logs 
            WHERE vehicle_id = :vehicle_id 
            ORDER BY service_date DESC 
            LIMIT 1
        """)
        try:
            result = db.execute(query, {"vehicle_id": vehicle_id}).mappings().first()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching latest maintenance log: {e}")
            raise e

    @staticmethod
    def insert_maintenance_log(db: Session, vehicle_id: str, issue: str, health_score: float) -> str:
        """
        Registers a new scheduled maintenance action.
        """
        query = text("""
            INSERT INTO maintenance_logs (vehicle_id, issue, health_score, service_date, status)
            VALUES (:vehicle_id, :issue, :health_score, NOW(), 'Scheduled')
            RETURNING id
        """)
        try:
            result = db.execute(
                query,
                {
                    "vehicle_id": vehicle_id,
                    "issue": issue,
                    "health_score": health_score
                }
            )
            log_id = result.scalar()
            db.commit()
            return str(log_id)
        except Exception as e:
            db.rollback()
            logger.error(f"Error inserting maintenance log: {e}")
            raise e

    @staticmethod
    def update_vehicle_health(db: Session, vehicle_id: str, health_score: float, status: str) -> None:
        """
        Updates the health score and operational status of a vehicle.
        """
        query = text("""
            UPDATE vehicles 
            SET health_score = :health_score, 
                status = :status 
            WHERE id = :vehicle_id
        """)
        try:
            db.execute(
                query,
                {
                    "health_score": health_score,
                    "status": status,
                    "vehicle_id": vehicle_id
                }
            )
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating vehicle status and health: {e}")
            raise e
