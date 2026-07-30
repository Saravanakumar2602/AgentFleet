from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("agentfleet.agents.compliance.service")

MAX_DRIVER_HOURS_PER_WEEK = 60
MAX_DAYS_SINCE_LAST_SERVICE = 90


class ComplianceService:
    """
    Business layer for Compliance Agent.
    Verifies driver weekly hours and vehicle last-service date from the database.
    """

    def check_compliance(self, db: Session, driver_id: str, vehicle_id: str) -> dict:
        """
        Validates regulatory compliance for driver hours and vehicle service intervals.
        """
        logger.info(f"Checking compliance: driver_id={driver_id}, vehicle_id={vehicle_id}")

        violations = []
        compliance_status = "Compliant"

        # 1. Driver hours this week
        driver_hours_week = 0.0
        try:
            is_sqlite = db.bind.dialect.name == "sqlite"
            if is_sqlite:
                row = db.execute(text("""
                    SELECT COALESCE(SUM(estimated_duration), 0) as total_minutes
                    FROM trips
                    WHERE driver_id = :driver_id
                    AND date(created_at) >= date('now', '-7 days')
                """), {"driver_id": driver_id}).first()
            else:
                row = db.execute(text("""
                    SELECT COALESCE(SUM(estimated_duration), 0) as total_minutes
                    FROM trips
                    WHERE driver_id = :driver_id
                    AND created_at >= NOW() - INTERVAL '7 days'
                """), {"driver_id": driver_id}).first()

            if row:
                driver_hours_week = round(float(row[0]) / 60.0, 1)
        except Exception as e:
            logger.warning(f"Failed to fetch driver hours: {e}")

        if driver_hours_week > MAX_DRIVER_HOURS_PER_WEEK:
            violations.append(f"Driver has logged {driver_hours_week}h this week, exceeding {MAX_DRIVER_HOURS_PER_WEEK}h limit.")

        # 2. Vehicle last service date
        days_since_service = 0
        last_service_date = "N/A"
        try:
            row = db.execute(text("""
                SELECT service_date FROM maintenance_logs
                WHERE vehicle_id = :vehicle_id
                ORDER BY service_date DESC LIMIT 1
            """), {"vehicle_id": vehicle_id}).first()

            if row and row[0]:
                svc_date = row[0]
                if isinstance(svc_date, str):
                    try:
                        svc_date = datetime.strptime(svc_date[:10], "%Y-%m-%d").date()
                    except Exception:
                        svc_date = None

                if svc_date:
                    days_since_service = (datetime.now().date() - svc_date).days
                    last_service_date = str(svc_date)
                    if days_since_service > MAX_DAYS_SINCE_LAST_SERVICE:
                        violations.append(
                            f"Vehicle last serviced {days_since_service} days ago, "
                            f"exceeding {MAX_DAYS_SINCE_LAST_SERVICE}-day service interval."
                        )
        except Exception as e:
            logger.warning(f"Failed to fetch vehicle service date: {e}")

        if violations:
            compliance_status = "Violation Detected"
            logger.warning(f"Compliance violations: {violations}")
        else:
            logger.info("Compliance check passed.")

        return {
            "driver_hours_this_week": driver_hours_week,
            "max_allowed_hours": MAX_DRIVER_HOURS_PER_WEEK,
            "last_vehicle_service_date": last_service_date,
            "days_since_last_service": days_since_service,
            "compliance_status": compliance_status,
            "violations": violations,
        }
