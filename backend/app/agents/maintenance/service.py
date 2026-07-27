from sqlalchemy.orm import Session
import logging

from backend.app.agents.maintenance.repository import MaintenanceRepository
from backend.app.shared.exceptions import VehicleUnavailableException

logger = logging.getLogger("agentfleet.agents.maintenance.service")

class MaintenanceService:
    """
    Business layer for Vehicle Health & Maintenance Agent.
    Strictly coordinates calculations, status checks, and logging triggers.
    """
    def __init__(self, repository: MaintenanceRepository = MaintenanceRepository()):
        self.repository = repository

    def evaluate_vehicle(self, db: Session, vehicle_id: str) -> dict:
        """
        Fetches vehicle, scores health metrics, logs urgent services,
        and returns payload dict matching contracts.
        """
        logger.info(f"Evaluating vehicle health: ID={vehicle_id}")

        # 1. Fetch vehicle
        vehicle = self.repository.get_vehicle(db, vehicle_id)
        if not vehicle:
            logger.warning(f"Vehicle not found in database: {vehicle_id}")
            raise VehicleUnavailableException("Vehicle not found.")

        # 2. Fetch latest maintenance history (stored for log traces/analytics)
        latest_log = self.repository.get_latest_maintenance(db, vehicle_id)
        if latest_log:
            logger.info(f"Found latest maintenance entry: status={latest_log['status']} dated {latest_log['service_date']}")

        # 3. Evaluate vehicle health score
        health_score = float(vehicle["health_score"]) if vehicle["health_score"] is not None else 100.0
        
        # Rule-based diagnostic scoring
        if health_score > 80:
            status = "Healthy"
            message = "Vehicle is healthy."
        elif 50 <= health_score <= 80:
            status = "Service Recommended"
            message = "Vehicle service recommended."
        else:
            status = "Maintenance Required"
            message = "Vehicle requires immediate maintenance."

        # 4. Estimate remaining service distance
        # Formula: (health_score - 50) * 50 km (valid for scores >= 50)
        remaining_service_distance = None
        if health_score >= 50:
            remaining_service_distance = int((health_score - 50) * 50)
        else:
            remaining_service_distance = 0

        # 5. Insert maintenance log and set status to Maintenance if required
        if status == "Maintenance Required":
            logger.warning(f"Vehicle {vehicle_id} health is critical ({health_score}). Scheduling immediate maintenance...")
            # Insert scheduled log entry
            self.repository.insert_maintenance_log(
                db=db,
                vehicle_id=vehicle_id,
                issue="Critical diagnostics check flag: health score below 50.",
                health_score=health_score
            )
            # Update vehicle status to 'Maintenance' in database
            self.repository.update_vehicle_health(
                db=db,
                vehicle_id=vehicle_id,
                health_score=health_score,
                status="Maintenance"
            )

        # 6. Formulate return payloads
        response_payload = {
            "vehicle_id": str(vehicle["id"]),
            "health_score": int(health_score),
            "vehicle_status": status,
            "message": message
        }

        if status != "Maintenance Required":
            response_payload["next_service_after_km"] = remaining_service_distance

        return response_payload
