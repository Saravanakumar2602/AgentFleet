from sqlalchemy.orm import Session
import logging
from sqlalchemy import text

from backend.app.workflows.base_workflow import BaseWorkflow
from backend.app.registry.registry import get_agent

logger = logging.getLogger("agentfleet.workflows.delivery_workflow")

class DeliveryWorkflow(BaseWorkflow):
    """
    Fleet Delivery Workflow orchestrating all 15 agents sequentially.
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
        # Step 1: Cargo Validation
        # --------------------------------------------------------------------
        agent_name = "Cargo Validation"
        try:
            logger.info("Executing Step 1: Cargo Validation Agent")
            cargo_agent = get_agent("cargo_validation")
            if not cargo_agent:
                raise RuntimeError("Cargo Validation Agent not found in registry.")
            cargo_res = cargo_agent.run(
                db=db,
                task_data={
                    "pickup": task_data["pickup"],
                    "destination": task_data["destination"],
                    "weight": float(task_data["weight"])
                }
            )
            steps_data["cargo_validation"] = cargo_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 2: Dispatch Agent
        # --------------------------------------------------------------------
        agent_name = "Dispatch"
        try:
            logger.info("Executing Step 2: Dispatch Agent")
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
        # Step 3: Traffic Agent
        # --------------------------------------------------------------------
        agent_name = "Traffic"
        try:
            logger.info("Executing Step 3: Traffic Agent")
            traffic_agent = get_agent("traffic")
            if not traffic_agent:
                raise RuntimeError("Traffic Agent not found in registry.")
            traffic_res = traffic_agent.run(
                db=db,
                task_data={
                    "pickup": task_data["pickup"],
                    "destination": task_data["destination"]
                }
            )
            steps_data["traffic"] = traffic_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 4: Weather Agent
        # --------------------------------------------------------------------
        agent_name = "Weather"
        try:
            logger.info("Executing Step 4: Weather Agent")
            weather_agent = get_agent("weather")
            if not weather_agent:
                raise RuntimeError("Weather Agent not found in registry.")
            weather_res = weather_agent.run(
                db=db,
                task_data={
                    "destination": task_data["destination"]
                }
            )
            steps_data["weather"] = weather_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 5: Route Agent
        # --------------------------------------------------------------------
        agent_name = "Route"
        try:
            logger.info("Executing Step 5: Route Agent")
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
            
            # Create a placeholder analytics record so the Analytics Agent has real records to calculate efficiency
            try:
                duration_str = route_res.get("estimated_duration", "0")
                minutes_val = 0
                if "h" in duration_str:
                    parts = duration_str.split("h")
                    hours_part = parts[0].strip()
                    mins_part = parts[1].replace("m", "").strip() if len(parts) > 1 else "0"
                    try:
                        minutes_val = int(hours_part) * 60 + int(mins_part or 0)
                    except:
                        minutes_val = 240
                else:
                    try:
                        minutes_val = int(duration_str.replace("m", "").strip())
                    except:
                        minutes_val = 240
                
                db.execute(text("""
                    INSERT INTO analytics (trip_id, fuel_used, average_speed, cost, delivery_time, created_at)
                    VALUES (:trip_id, :fuel_used, :average_speed, :cost, :delivery_time, now())
                """), {
                    "trip_id": checkpoint_data["trip_id"],
                    "fuel_used": route_res["estimated_fuel"],
                    "average_speed": 61.26,
                    "cost": round(route_res["estimated_fuel"] * 1.15, 2),
                    "delivery_time": minutes_val
                })
                db.commit()
            except Exception as analytics_err:
                logger.warning(f"Failed to create placeholder analytics record: {analytics_err}")
                db.rollback()

            # Outbound Email Notification to Driver
            try:
                from backend.app.core.config import settings
                from backend.app.shared.notifications.email import send_email_async
                
                driver_email = settings.DEMO_DRIVER_EMAIL or "saravanaegs2602@gmail.com"
                driver_name = dispatch_res.get("driver", {}).get("name", "Driver")
                
                # Fetch database driver email if exists
                driver_res = db.execute(text("""
                    SELECT u.email 
                    FROM drivers d 
                    JOIN users u ON d.user_id = u.id 
                    WHERE d.id = :driver_id
                """), {"driver_id": checkpoint_data["driver_id"]}).first()
                if driver_res and driver_res[0] and not driver_res[0].endswith("agentfleet.com"):
                    driver_email = driver_res[0]

                if driver_email:
                    pickup = task_data["pickup"]
                    destination = task_data["destination"]
                    gmaps_url = f"https://www.google.com/maps/dir/?api=1&origin={pickup}&destination={destination}"
                    
                    subject = f"[AgentFleet] New Trip Assignment: {pickup} to {destination}"
                    html_body = f"""
                    <html>
                      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                          <h2 style="color: #4f8ef7; border-bottom: 2px solid #4f8ef7; padding-bottom: 10px;">New Cargo Dispatch Assignment</h2>
                          <p>Hello <strong>{driver_name}</strong>,</p>
                          <p>You have been assigned to transport cargo for the following route:</p>
                          <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                            <tr>
                              <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold; width: 150px;">Pickup Coordinates:</td>
                              <td style="padding: 8px; border-bottom: 1px solid #eee;">{pickup}</td>
                            </tr>
                            <tr>
                              <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Destination:</td>
                              <td style="padding: 8px; border-bottom: 1px solid #eee;">{destination}</td>
                            </tr>
                            <tr>
                              <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Distance:</td>
                              <td style="padding: 8px; border-bottom: 1px solid #eee;">{route_res.get('distance_km', 0.0)} km</td>
                            </tr>
                            <tr>
                              <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Est. Duration:</td>
                              <td style="padding: 8px; border-bottom: 1px solid #eee;">{route_res.get('estimated_duration', 'N/A')}</td>
                            </tr>
                            <tr>
                              <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Est. Fuel:</td>
                              <td style="padding: 8px; border-bottom: 1px solid #eee;">{route_res.get('estimated_fuel', 0.0)} L</td>
                            </tr>
                          </table>
                          <div style="margin: 25px 0; text-align: center;">
                            <a href="{gmaps_url}" target="_blank" 
                               style="background-color: #4f8ef7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                               Start Navigation on Google Maps
                            </a>
                          </div>
                          <p style="font-size: 12px; color: #666; border-top: 1px solid #eee; padding-top: 15px;">
                            This is an automated dispatch alert sent from the AgentFleet supervisor system. Please contact customer support if you notice any discrepancies.
                          </p>
                        </div>
                      </body>
                    </html>
                    """
                    text_body = f"Hello {driver_name},\n\nYou have been assigned to a new cargo transport.\nRoute: {pickup} to {destination}\nDistance: {route_res.get('distance_km')} km\nETA: {route_res.get('estimated_duration')}\nStart Google Maps Navigation: {gmaps_url}"
                    
                    send_email_async(driver_email, subject, html_body, text_body)
            except Exception as email_dispatch_err:
                logger.warning(f"Outbound driver notification error: {email_dispatch_err}")

        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 6: ETA Updater Agent
        # --------------------------------------------------------------------
        agent_name = "ETA Updater"
        try:
            logger.info("Executing Step 6: ETA Updater Agent")
            eta_agent = get_agent("eta_updater")
            if not eta_agent:
                raise RuntimeError("ETA Updater Agent not found in registry.")

            # Base duration from route is string, let's parse or use fallback
            duration_str = route_res.get("estimated_duration", "0")
            minutes_val = 0
            if "h" in duration_str:
                parts = duration_str.split("h")
                hours_part = parts[0].strip()
                mins_part = parts[1].replace("m", "").strip() if len(parts) > 1 else "0"
                try:
                    minutes_val = int(hours_part) * 60 + int(mins_part or 0)
                except:
                    minutes_val = 240
            else:
                try:
                    minutes_val = int(duration_str.replace("m", "").strip())
                except:
                    minutes_val = 240

            eta_res = eta_agent.run(
                db=db,
                task_data={
                    "base_duration_minutes": minutes_val,
                    "traffic_delay_minutes": traffic_res.get("delay_minutes", 0),
                    "weather_delay_minutes": weather_res.get("weather_delay_minutes", 0)
                }
            )
            steps_data["eta_updater"] = eta_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 7: Compliance Agent
        # --------------------------------------------------------------------
        agent_name = "Compliance"
        try:
            logger.info("Executing Step 7: Compliance Agent")
            compliance_agent = get_agent("compliance")
            if not compliance_agent:
                raise RuntimeError("Compliance Agent not found in registry.")
            compliance_res = compliance_agent.run(
                db=db,
                task_data={
                    "driver_id": checkpoint_data["driver_id"],
                    "vehicle_id": checkpoint_data["vehicle_id"]
                }
            )
            steps_data["compliance"] = compliance_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 8: Maintenance Agent
        # --------------------------------------------------------------------
        agent_name = "Maintenance"
        try:
            logger.info("Executing Step 8: Maintenance Agent")
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
        # Step 9: Fuel Agent
        # --------------------------------------------------------------------
        agent_name = "Fuel"
        try:
            logger.info("Executing Step 9: Fuel Agent")
            fuel_agent = get_agent("fuel")
            if not fuel_agent:
                raise RuntimeError("Fuel Agent not found in registry.")
            fuel_res = fuel_agent.run(
                db=db,
                task_data={
                    "vehicle_id": checkpoint_data["vehicle_id"],
                    "distance_km": float(route_res.get("distance_km", 0)),
                    "estimated_fuel_liters": float(route_res.get("estimated_fuel", 0))
                }
            )
            steps_data["fuel"] = fuel_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 10: Fleet Analytics Agent
        # --------------------------------------------------------------------
        agent_name = "Analytics"
        try:
            logger.info("Executing Step 10: Fleet Analytics Agent")
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
        # Step 11: Driver Rating Agent
        # --------------------------------------------------------------------
        agent_name = "Driver Rating"
        try:
            logger.info("Executing Step 11: Driver Rating Agent")
            driver_rating_agent = get_agent("driver_rating")
            if not driver_rating_agent:
                raise RuntimeError("Driver Rating Agent not found in registry.")
            rating_res = driver_rating_agent.run(
                db=db,
                task_data={
                    "driver_id": checkpoint_data["driver_id"]
                }
            )
            steps_data["driver_rating"] = rating_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 12: Customer Agent
        # --------------------------------------------------------------------
        agent_name = "Customer"
        try:
            logger.info("Executing Step 12: Customer Agent")
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

        # --------------------------------------------------------------------
        # Step 13: Invoice Agent
        # --------------------------------------------------------------------
        agent_name = "Invoice"
        try:
            logger.info("Executing Step 13: Invoice Agent")
            invoice_agent = get_agent("invoice")
            if not invoice_agent:
                raise RuntimeError("Invoice Agent not found in registry.")
            invoice_res = invoice_agent.run(
                db=db,
                task_data={
                    "trip_id": checkpoint_data["trip_id"],
                    "distance_km": float(route_res.get("distance_km", 0)),
                    "fuel_cost_inr": float(fuel_res.get("estimated_fuel_cost_inr", 0))
                }
            )
            steps_data["invoice"] = invoice_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 14: Fleet Summary Agent
        # --------------------------------------------------------------------
        agent_name = "Fleet Summary"
        try:
            logger.info("Executing Step 14: Fleet Summary Agent")
            summary_agent = get_agent("fleet_summary")
            if not summary_agent:
                raise RuntimeError("Fleet Summary Agent not found in registry.")
            summary_res = summary_agent.run(
                db=db,
                task_data={}
            )
            steps_data["fleet_summary"] = summary_res
        except Exception as exc:
            self.rollback(db, checkpoint_data)
            return self._build_failure_response(agent_name, exc)

        # --------------------------------------------------------------------
        # Step 15: SOS Alert Agent
        # --------------------------------------------------------------------
        agent_name = "SOS Alert"
        try:
            logger.info("Executing Step 15: SOS Alert Agent")
            sos_agent = get_agent("sos_alert")
            if not sos_agent:
                raise RuntimeError("SOS Alert Agent not found in registry.")
            sos_res = sos_agent.run(
                db=db,
                task_data={
                    "weather_risk": weather_res.get("weather_risk", "Low"),
                    "health_score": int(maint_res.get("health_score", 100)),
                    "vehicle_id": checkpoint_data["vehicle_id"],
                    "trip_id": checkpoint_data["trip_id"]
                }
            )
            steps_data["sos_alert"] = sos_res
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
            if trip_id:
                db.execute(text("DELETE FROM notifications WHERE trip_id = :trip_id"), {"trip_id": trip_id})
                db.execute(text("DELETE FROM invoices WHERE trip_id = :trip_id"), {"trip_id": trip_id})
                db.execute(text("DELETE FROM trips WHERE id = :id"), {"id": trip_id})
            if vehicle_id:
                db.execute(text("UPDATE vehicles SET status = 'Available' WHERE id = :id"), {"id": vehicle_id})
            if driver_id:
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
        
        # New 10 agents
        cargo_res = steps_data["cargo_validation"]
        traffic_res = steps_data["traffic"]
        weather_res = steps_data["weather"]
        eta_res = steps_data["eta_updater"]
        comp_res = steps_data["compliance"]
        fuel_res = steps_data["fuel"]
        rating_res = steps_data["driver_rating"]
        invoice_res = steps_data["invoice"]
        summary_res = steps_data["fleet_summary"]
        sos_res = steps_data["sos_alert"]

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
            "customer_message": customer_res["customer_message"],
            
            # Formatted new properties
            "cargo_validation": cargo_res,
            "traffic": traffic_res,
            "weather": weather_res,
            "eta_updater": eta_res,
            "compliance": comp_res,
            "fuel": fuel_res,
            "driver_rating": rating_res,
            "invoice": invoice_res,
            "fleet_summary": summary_res,
            "sos_alert": sos_res
        }

    def _build_failure_response(self, failed_agent: str, exc: Exception) -> dict:
        logger.warning(f"Workflow execution halted. Agent '{failed_agent}' failed.")
        reason = exc.message if hasattr(exc, "message") else str(exc)
        return {
            "status": "failed",
            "failed_agent": failed_agent,
            "reason": reason
        }
