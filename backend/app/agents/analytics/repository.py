from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger("agentfleet.agents.analytics.repository")

class AnalyticsRepository:
    """
    Data Access Object for Fleet Analytics Agent executing direct SQL queries.
    """
    @staticmethod
    def get_vehicle(db: Session, vehicle_id: str) -> dict | None:
        """
        Fetches basic vehicle attributes. Resolves non-UUID or mock IDs to vehicle numbers.
        """
        import uuid
        is_uuid = False
        try:
            uuid.UUID(str(vehicle_id))
            is_uuid = True
        except ValueError:
            pass

        if is_uuid:
            query = text("""
                SELECT id, vehicle_number, vehicle_type, health_score 
                FROM vehicles 
                WHERE id = :vehicle_id
            """)
            try:
                result = db.execute(query, {"vehicle_id": vehicle_id}).mappings().first()
                return dict(result) if result else None
            except Exception as e:
                logger.error(f"Error fetching vehicle details: {e}")
                raise e
        else:
            mapping = {
                "v1": "TN38AB1234",
                "v2": "TN38CD5678",
                "v3": "TN38EF9012",
                "v4": "KA-RT-8011",
                "v5": "MH12AB3456",
                "v6": "TN45GH7890"
            }
            lookup_val = mapping.get(vehicle_id, vehicle_id)
            query = text("""
                SELECT id, vehicle_number, vehicle_type, health_score 
                FROM vehicles 
                WHERE vehicle_number = :lookup_val
            """)
            try:
                result = db.execute(query, {"lookup_val": lookup_val}).mappings().first()
                return dict(result) if result else None
            except Exception as e:
                logger.error(f"Error fetching vehicle details by number: {e}")
                raise e

    @staticmethod
    def get_trip_statistics(db: Session, vehicle_id: str) -> dict:
        """
        Retrieves total trips, averages, and distance totals for a vehicle.
        """
        query = text("""
            SELECT 
                COUNT(t.id) AS total_trips,
                COALESCE(AVG(t.distance_km), 0.0) AS avg_distance,
                COALESCE(SUM(t.distance_km), 0.0) AS total_distance,
                COALESCE(AVG(a.fuel_used), 0.0) AS avg_fuel,
                COALESCE(SUM(a.fuel_used), 0.0) AS total_fuel
            FROM trips t
            LEFT JOIN analytics a ON a.trip_id = t.id
            WHERE t.vehicle_id = :vehicle_id
        """)
        try:
            result = db.execute(query, {"vehicle_id": vehicle_id}).mappings().first()
            return dict(result) if result else {
                "total_trips": 0,
                "avg_distance": 0.0,
                "total_distance": 0.0,
                "avg_fuel": 0.0,
                "total_fuel": 0.0
            }
        except Exception as e:
            logger.error(f"Error fetching trip statistics: {e}")
            raise e

    @staticmethod
    def get_maintenance_statistics(db: Session, vehicle_id: str) -> int:
        """
        Counts all maintenance log entries for a vehicle.
        """
        query = text("""
            SELECT COUNT(id) 
            FROM maintenance_logs 
            WHERE vehicle_id = :vehicle_id
        """)
        try:
            result = db.execute(query, {"vehicle_id": vehicle_id}).scalar()
            return int(result) if result is not None else 0
        except Exception as e:
            logger.error(f"Error counting maintenance logs: {e}")
            raise e

    @staticmethod
    def get_fleet_average_fuel_efficiency(db: Session) -> float:
        """
        Computes fleet-wide average fuel efficiency: total distance / total fuel.
        """
        query = text("""
            SELECT 
                COALESCE(SUM(t.distance_km) / NULLIF(SUM(a.fuel_used), 0.0), 0.0)
            FROM trips t
            JOIN analytics a ON a.trip_id = t.id
        """)
        try:
            result = db.execute(query).scalar()
            return float(result) if result is not None else 0.0
        except Exception as e:
            logger.error(f"Error computing fleet average fuel efficiency: {e}")
            raise e
