from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger("agentfleet.agents.driver_rating.service")


class DriverRatingService:
    """
    Business layer for Driver Rating Agent.
    Scores driver performance 0-100 based on trip history from the database.
    Optionally persists the score back to the drivers table.
    """

    def rate_driver(self, db: Session, driver_id: str) -> dict:
        """
        Computes a composite driver performance score.
        """
        logger.info(f"Rating driver: driver_id={driver_id}")

        # 1. Trip statistics
        total_trips = 0
        avg_distance = 0.0
        total_distance = 0.0
        try:
            row = db.execute(text("""
                SELECT COUNT(*) as total_trips,
                       COALESCE(AVG(distance_km), 0) as avg_distance,
                       COALESCE(SUM(distance_km), 0) as total_distance
                FROM trips WHERE driver_id = :driver_id
            """), {"driver_id": driver_id}).first()
            if row:
                total_trips = int(row[0])
                avg_distance = round(float(row[1]), 1)
                total_distance = float(row[2])
        except Exception as e:
            logger.warning(f"Failed to fetch driver trip stats: {e}")

        # 2. Maintenance-free km (trips completed without maintenance stops)
        maintenance_count = 0
        try:
            row = db.execute(text("""
                SELECT COUNT(*) FROM maintenance_logs ml
                JOIN trips t ON t.vehicle_id = ml.vehicle_id
                WHERE t.driver_id = :driver_id
            """), {"driver_id": driver_id}).first()
            if row:
                maintenance_count = int(row[0])
        except Exception as e:
            logger.warning(f"Failed to fetch maintenance count for driver: {e}")

        # 3. Scoring algorithm (0-100)
        # Base: 50 points
        # +trip_count bonus (capped at 20): min(total_trips * 2, 20)
        # +distance bonus (capped at 20): min(total_distance / 500, 20)
        # -maintenance penalty: min(maintenance_count * 5, 30)
        score = 50
        score += min(total_trips * 2, 20)
        score += min(int(total_distance / 500), 20)
        score -= min(maintenance_count * 5, 30)
        score = max(0, min(100, score))

        # 4. Grade
        if score >= 90:
            grade = "A+"
            feedback = "Excellent performance. Top-tier driver."
        elif score >= 75:
            grade = "A"
            feedback = "Good driver. Consistent performance."
        elif score >= 60:
            grade = "B"
            feedback = "Average performance. Monitor fuel efficiency."
        elif score >= 40:
            grade = "C"
            feedback = "Below average. Frequent maintenance incidents detected."
        else:
            grade = "D"
            feedback = "Poor performance. Immediate coaching recommended."

        # 5. Persist score to drivers table (add column if not exists)
        try:
            try:
                db.execute(text("ALTER TABLE drivers ADD COLUMN driver_score INTEGER DEFAULT 0"))
                db.commit()
            except Exception:
                pass  # Column already exists

            db.execute(text("""
                UPDATE drivers SET driver_score = :score WHERE id = :driver_id
            """), {"score": score, "driver_id": driver_id})
            db.commit()
            logger.info(f"Driver score {score} persisted for driver {driver_id}")
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to persist driver score: {e}")

        return {
            "driver_id": driver_id,
            "total_trips": total_trips,
            "total_distance_km": round(total_distance, 1),
            "avg_distance_km": avg_distance,
            "maintenance_incidents": maintenance_count,
            "driver_score": score,
            "performance_grade": grade,
            "feedback": feedback,
        }
