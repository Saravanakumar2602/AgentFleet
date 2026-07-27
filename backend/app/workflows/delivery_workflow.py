from sqlalchemy.orm import Session
import logging

from backend.app.workflows.base_workflow import BaseWorkflow
from backend.app.registry.registry import get_agent

logger = logging.getLogger("agentfleet.workflows.delivery_workflow")

class DeliveryWorkflow(BaseWorkflow):
    """
    Fleet Delivery Workflow orchestrating all 5 agents sequentially:
    Dispatch -> Route -> Maintenance -> Analytics -> Customer.
    """
    def validate(self, task_data: dict) -> bool:
        pickup = task_data.get("pickup")
        destination = task_data.get("destination")
        weight = task_data.get("weight")

        if not all([pickup, destination, weight]):
            raise ValueError("Invalid workflow inputs. 'pickup', 'destination', and 'weight' are required.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        checkpoint_data = {}
        steps_data = {}

        # --------------------------------------------------------------------
        # Step 1: Dispatch Agent
        # --------------------------------------------------------------------
        agent_name = "Dispatch"
        try:
            logger.info("Executing Step 1: Dispatch Agent")
            dispatch_agent = get_agent("dispatch")
            if not dispatch_agent:
                raise RuntimeError("Dispatch Agent not found in registry.")

            dispatch_res = dispatch_agent.run(
                db=db,
                task_data={
                    "pickup": task_data["pickup"],
                    "destination": task_data["destination"],
                    "weight": float(task_data["weight"])
                }
            )
            steps_data["dispatch"] = dispatch_res
            
            # Setup rollback checkpoints
            checkpoint_data["trip_id"] = dispatch_res["trip_id"]
            checkpoint_data["vehicle_id"] = dispatch_res["vehicle"]["id"]
            checkpoint_data["driver_id"] = dispatch_res["driver"]["id"]
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 2: Route Agent
        # --------------------------------------------------------------------
        agent_name = "Route"
        try:
            logger.info("Executing Step 2: Route Agent")
            route_agent = get_agent("route")
            if not route_agent:
                raise RuntimeError("Route Agent not found in registry.")

            route_res = route_agent.run(
                db=db,
                task_data={
                    "vehicle_id": checkpoint_data["vehicle_id"],
                    "pickup": task_data["pickup"],
                    "destination": task_data["destination"]
                }
            )
            steps_data["route"] = route_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 3: Maintenance Agent
        # --------------------------------------------------------------------
        agent_name = "Maintenance"
        try:
            logger.info("Executing Step 3: Maintenance Agent")
            maint_agent = get_agent("maintenance")
            if not maint_agent:
                raise RuntimeError("Maintenance Agent not found in registry.")

            maint_res = maint_agent.run(
                db=db,
                task_data={
                    "vehicle_id": checkpoint_data["vehicle_id"]
                }
            )
            steps_data["maintenance"] = maint_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 4: Fleet Analytics Agent
        # --------------------------------------------------------------------
        agent_name = "Analytics"
        try:
            logger.info("Executing Step 4: Fleet Analytics Agent")
            analytics_agent = get_agent("analytics")
            if not analytics_agent:
                raise RuntimeError("Analytics Agent not found in registry.")

            analytics_res = analytics_agent.run(
                db=db,
                task_data={
                    "vehicle_id": checkpoint_data["vehicle_id"]
                }
            )
            steps_data["analytics"] = analytics_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 5: Customer Agent
        # --------------------------------------------------------------------
        agent_name = "Customer"
        try:
            logger.info("Executing Step 5: Customer Agent")
            customer_agent = get_agent("customer")
            if not customer_agent:
                raise RuntimeError("Customer Agent not found in registry.")

            customer_res = customer_agent.run(
                db=db,
                task_data={
                    "trip_id": checkpoint_data["trip_id"]
                }
            )
            steps_data["customer"] = customer_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # Merge every response and return formatted unified success response
        return self.format_result(steps_data)

    def rollback(self, db: Session, checkpoint_data: dict) -> None:
        """
        Reverts database changes made by Dispatch agent if later stages fail.
        """
        trip_id = checkpoint_data.get("trip_id")
        vehicle_id = checkpoint_data.get("vehicle_id")
        driver_id = checkpoint_data.get("driver_id")

        if not trip_id and not vehicle_id and not driver_id:
            return

        logger.info(f"Triggering workflow rollback for checkpoint state: {checkpoint_data}")
        try:
            from sqlalchemy import text
            if trip_id:
                # Delete the created trip record to prevent orphaned rows
                db.execute(text("DELETE FROM trips WHERE id = :id"), {"id": trip_id})
            if vehicle_id:
                # Reset vehicle status back to 'Available'
                db.execute(text("UPDATE vehicles SET status = 'Available' WHERE id = :id"), {"id": vehicle_id})
            if driver_id:
                # Reset driver status back to 'Available'
                db.execute(text("UPDATE drivers SET status = 'Available' WHERE id = :id"), {"id": driver_id})
            db.commit()
            logger.info("Workflow rollback executed successfully.")
        except Exception as rollback_err:
            db.rollback()
            logger.error(f"Rollback execution failed: {rollback_err}")

    def format_result(self, steps_data: dict) -> dict:
        dispatch_res = steps_data["dispatch"]
        route_res = steps_data["route"]
        maint_res = steps_data["maintenance"]
        analytics_res = steps_data["analytics"]
        customer_res = steps_data["customer"]

        return {
            "status": "success",
            "agent": "Fleet Delivery Workflow",
            "trip_id": dispatch_res["trip_id"],
            "vehicle": dispatch_res["vehicle"],
            "driver": dispatch_res["driver"],
            "distance_km": route_res["distance_km"],
            "estimated_duration": route_res["estimated_duration"],
            "estimated_fuel": route_res["estimated_fuel"],
            "health_score": maint_res["health_score"],
            "vehicle_status": maint_res["vehicle_status"],
            "next_service_after_km": maint_res.get("next_service_after_km"),
            "utilization": analytics_res["utilization"],
            "recommendation": analytics_res["recommendation"],
            "customer_message": customer_res["customer_message"]
        }

    def _build_failure_response(self, failed_agent: str, exc: Exception) -> dict:
        logger.warning(f"Workflow execution halted. Agent '{failed_agent}' failed.")
        reason = exc.message if hasattr(exc, "message") else str(exc)
        return {
            "status": "failed",
            "failed_agent": failed_agent,
            "reason": reason
        }
