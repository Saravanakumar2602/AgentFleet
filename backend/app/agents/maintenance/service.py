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

        real_vehicle_id = str(vehicle["id"])

        # 2. Fetch latest maintenance history (stored for log traces/analytics)
        latest_log = self.repository.get_latest_maintenance(db, real_vehicle_id)
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
            logger.warning(f"Vehicle {real_vehicle_id} health is critical ({health_score}). Scheduling immediate maintenance...")
            # Insert scheduled log entry
            self.repository.insert_maintenance_log(
                db=db,
                vehicle_id=real_vehicle_id,
                issue="Critical diagnostics check flag: health score below 50.",
                health_score=health_score
            )
            # Update vehicle status to 'Maintenance' in database
            self.repository.update_vehicle_health(
                db=db,
                vehicle_id=real_vehicle_id,
                health_score=health_score,
                status="Maintenance"
            )

            # Trigger Outbound Email Notification to the Driver
            try:
                from backend.app.core.config import settings
                from backend.app.shared.notifications.email import send_email_async
                from sqlalchemy import text
                
                driver_email = settings.DEMO_DRIVER_EMAIL or "saravanaegs2602@gmail.com"
                driver_name = "Driver"
                
                # Retrieve current driver username and email
                driver_res = db.execute(text("""
                    SELECT u.name, u.email 
                    FROM vehicles v
                    JOIN drivers d ON v.current_driver_id = d.id
                    JOIN users u ON d.user_id = u.id
                    WHERE v.id = :vehicle_id
                """), {"vehicle_id": real_vehicle_id}).first()
                if driver_res:
                    name, db_email = driver_res
                    if name:
                        driver_name = name
                    if db_email and not db_email.endswith("agentfleet.com"):
                        driver_email = db_email

                if driver_email:
                    subject = f"[AgentFleet] Action Required: Vehicle {vehicle['vehicle_number']} Scheduled for Maintenance"
                    html_body = f"""
                    <html>
                      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                          <h2 style="color: #e11d48; border-bottom: 2px solid #e11d48; padding-bottom: 10px;">Critical Vehicle Diagnostics Alert</h2>
                          <p>Hello <strong>{driver_name}</strong>,</p>
                          <p>Your assigned vehicle (License Plate: <strong>{vehicle['vehicle_number']}</strong>) has failed the diagnostics health check.</p>
                          <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                            <tr>
                              <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold; width: 150px;">Diagnostics Score:</td>
                              <td style="padding: 8px; border-bottom: 1px solid #eee; color: #e11d48; font-weight: bold;">{int(health_score)} / 100</td>
                            </tr>
                            <tr>
                              <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Current Status:</td>
                              <td style="padding: 8px; border-bottom: 1px solid #eee; color: #d97706; font-weight: bold;">Scheduled for Servicing</td>
                            </tr>
                            <tr>
                              <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Diagnostic Issue:</td>
                              <td style="padding: 8px; border-bottom: 1px solid #eee;">Critical diagnostics check flag: health score below 50.</td>
                            </tr>
                          </table>
                          <p style="background-color: #fff1f2; border-left: 4px solid #e11d48; padding: 12px; border-radius: 4px; color: #9f1239; font-weight: 500;">
                            <strong>IMPORTANT:</strong> This vehicle has been marked 'Maintenance' in the database and is temporarily disabled for incoming cargo assignments. Please deliver it to the fleet service garage immediately.
                          </p>
                          <p style="font-size: 12px; color: #666; border-top: 1px solid #eee; padding-top: 15px; margin-top: 25px;">
                            This is an automated alerts notification sent from the AgentFleet diagnostics supervisor.
                          </p>
                        </div>
                      </body>
                    </html>
                    """
                    text_body = f"Hello {driver_name},\n\nYour assigned vehicle {vehicle['vehicle_number']} health score is critical ({int(health_score)}). It has been scheduled for servicing and disabled for dispatches."
                    
                    send_email_async(driver_email, subject, html_body, text_body)
            except Exception as email_err:
                logger.warning(f"Failed to dispatch maintenance email alert: {email_err}")

        # 6. Formulate return payloads
        response_payload = {
            "agent": "Maintenance Agent",
            "vehicle_id": str(vehicle["id"]),
            "health_score": int(health_score),
            "vehicle_status": status,
            "message": message
        }

        if status != "Maintenance Required":
            response_payload["next_service_after_km"] = remaining_service_distance

        return response_payload
