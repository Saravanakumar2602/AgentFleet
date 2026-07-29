from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from datetime import datetime

from backend.app.workflows.base_workflow import BaseWorkflow
from backend.app.shared.exceptions import AgentFleetException

logger = logging.getLogger("agentfleet.workflows.complete_trip_workflow")

class CompleteTripWorkflow(BaseWorkflow):
    """
    Trip Completion Workflow:
    Updates Trip status to 'Completed' and sets Vehicle & Driver back to 'Available'.
    """
    def validate(self, task_data: dict) -> bool:
        trip_id = task_data.get("trip_id")
        vehicle_number = task_data.get("vehicle_number")

        if not trip_id and not vehicle_number:
            raise ValueError("Invalid workflow inputs. 'trip_id' or 'vehicle_number' is required to complete a trip.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        trip_id = task_data.get("trip_id")
        vehicle_number = task_data.get("vehicle_number")
        
        # 1. Resolve trip from DB
        trip = None
        if trip_id:
            query = text("SELECT id, vehicle_id, driver_id, status FROM trips WHERE id = :id LIMIT 1")
            trip = db.execute(query, {"id": trip_id}).mappings().first()
        elif vehicle_number:
            # Find active trip by vehicle number
            query = text("""
                SELECT t.id, t.vehicle_id, t.driver_id, t.status 
                FROM trips t
                JOIN vehicles v ON t.vehicle_id = v.id
                WHERE v.vehicle_number = :num AND t.status IN ('Assigned', 'Pending', 'In Transit', 'Route Generated')
                ORDER BY t.created_at DESC
                LIMIT 1
            """)
            trip = db.execute(query, {"num": vehicle_number.strip().upper()}).mappings().first()

        if not trip:
            logger.warning("No active trip found to complete.")
            raise AgentFleetException("No active trip found for completion.", status_code=404)

        trip_dict = dict(trip)
        checkpoint_data = {
            "trip_id": str(trip_dict["id"]),
            "vehicle_id": str(trip_dict["vehicle_id"]) if trip_dict["vehicle_id"] else None,
            "driver_id": str(trip_dict["driver_id"]) if trip_dict["driver_id"] else None,
            "original_status": trip_dict["status"]
        }

        # 2. Complete Trip and release assets in a transaction block
        try:
            # Update trip status
            db.execute(
                text("UPDATE trips SET status = 'Completed', completed_at = NOW() WHERE id = :id"),
                {"id": trip_dict["id"]}
            )
            
            # Release vehicle
            if trip_dict["vehicle_id"]:
                db.execute(
                    text("UPDATE vehicles SET status = 'Available' WHERE id = :id"),
                    {"id": trip_dict["vehicle_id"]}
                )
                
            # Release driver
            if trip_dict["driver_id"]:
                db.execute(
                    text("UPDATE drivers SET status = 'Available' WHERE id = :id"),
                    {"id": trip_dict["driver_id"]}
                )
                
            db.commit()
            logger.info(f"Trip {trip_dict['id']} completed and assets released successfully.")
        except Exception as exc:
            db.rollback()
            logger.error(f"Failed to execute database transactions for trip completion: {exc}")
            raise exc

        # 3. Fetch completed stats for response formatting
        vehicle_num = "N/A"
        driver_name = "N/A"
        if trip_dict["vehicle_id"]:
            row = db.execute(text("SELECT vehicle_number FROM vehicles WHERE id = :id"), {"id": trip_dict["vehicle_id"]}).first()
            if row:
                vehicle_num = row[0]
        if trip_dict["driver_id"]:
            row = db.execute(text("SELECT u.name FROM drivers d JOIN users u ON d.user_id = u.id WHERE d.id = :id"), {"id": trip_dict["driver_id"]}).first()
            if row:
                driver_name = row[0]

        steps_data = {
            "trip_id": str(trip_dict["id"]),
            "vehicle_number": vehicle_num,
            "driver_name": driver_name,
            "status": "Completed"
        }

        return self.format_result(steps_data)

    def rollback(self, db: Session, checkpoint_data: dict) -> None:
        """
        Reverts trip completion state to original status if error occurs.
        """
        trip_id = checkpoint_data.get("trip_id")
        vehicle_id = checkpoint_data.get("vehicle_id")
        driver_id = checkpoint_data.get("driver_id")
        original_status = checkpoint_data.get("original_status", "Assigned")

        if not trip_id:
            return

        logger.info(f"Rolling back trip completion for trip: {trip_id}")
        try:
            db.execute(
                text("UPDATE trips SET status = :status, completed_at = NULL WHERE id = :id"),
                {"status": original_status, "id": trip_id}
            )
            if vehicle_id:
                db.execute(
                    text("UPDATE vehicles SET status = 'Busy' WHERE id = :id"),
                    {"id": vehicle_id}
                )
            if driver_id:
                db.execute(
                    text("UPDATE drivers SET status = 'Busy' WHERE id = :id"),
                    {"id": driver_id}
                )
            db.commit()
        except Exception as rollback_err:
            db.rollback()
            logger.error(f"Rollback of trip completion failed: {rollback_err}")

    def format_result(self, steps_data: dict) -> dict:
        return {
            "status": "success",
            "agent": "Complete Trip Workflow",
            "trip_id": steps_data["trip_id"],
            "vehicle_number": steps_data["vehicle_number"],
            "driver_name": steps_data["driver_name"],
            "message": f"Trip {steps_data['trip_id']} completed successfully. Vehicle {steps_data['vehicle_number']} and driver {steps_data['driver_name']} are now Available."
        }
