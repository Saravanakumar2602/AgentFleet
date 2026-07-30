from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger("agentfleet.agents.fleet_summary.service")


class FleetSummaryService:
    """
    Business layer for Fleet Summary Agent.
    Aggregates fleet-wide KPIs from the database.
    """

    def generate_summary(self, db: Session) -> dict:
        """
        Queries aggregate fleet metrics and returns a KPI summary.
        """
        logger.info("Generating fleet-wide summary")

        total_vehicles = 0
        active_trips = 0
        available_vehicles = 0
        avg_health_score = 0.0
        maintenance_vehicles = 0
        total_trips_all_time = 0
        total_revenue_inr = 0.0
        fleet_utilization_pct = 0

        try:
            row = db.execute(text("""
                SELECT COUNT(*),
                       SUM(CASE WHEN status != 'Available' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END),
                       COALESCE(AVG(health_score), 100),
                       SUM(CASE WHEN status = 'Maintenance' THEN 1 ELSE 0 END)
                FROM vehicles
            """)).first()
            if row:
                total_vehicles = int(row[0] or 0)
                active_trips = int(row[1] or 0)
                available_vehicles = int(row[2] or 0)
                avg_health_score = round(float(row[3] or 100), 1)
                maintenance_vehicles = int(row[4] or 0)

            total_trips_all_time = db.execute(text("SELECT COUNT(*) FROM trips")).scalar() or 0

            # Estimate revenue from invoices if table exists
            try:
                total_revenue_inr = db.execute(
                    text("SELECT COALESCE(SUM(total_amount), 0) FROM invoices")
                ).scalar() or 0.0
                total_revenue_inr = round(float(total_revenue_inr), 2)
            except Exception:
                total_revenue_inr = 0.0

            fleet_utilization_pct = (
                round((active_trips / total_vehicles) * 100) if total_vehicles > 0 else 0
            )
        except Exception as e:
            logger.warning(f"Fleet summary query failed: {e}")

        logger.info(
            f"Fleet summary: total={total_vehicles}, active={active_trips}, "
            f"utilization={fleet_utilization_pct}%, avg_health={avg_health_score}"
        )

        return {
            "total_vehicles": total_vehicles,
            "active_trips": active_trips,
            "available_vehicles": available_vehicles,
            "maintenance_vehicles": maintenance_vehicles,
            "avg_fleet_health_score": avg_health_score,
            "total_trips_all_time": int(total_trips_all_time),
            "total_revenue_inr": total_revenue_inr,
            "fleet_utilization_pct": fleet_utilization_pct,
        }
