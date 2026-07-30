from sqlalchemy.orm import Session
import logging

logger = logging.getLogger("agentfleet.agents.sos_alert.service")


class SosAlertService:
    """
    Business layer for SOS / Emergency Alert Agent.
    Triggers an alert email to the fleet manager if weather or vehicle health is critical.
    """

    def check_and_alert(
        self,
        db: Session,
        weather_risk: str,
        health_score: int,
        vehicle_id: str,
        trip_id: str,
    ) -> dict:
        """
        Evaluates risk factors and sends an alert email if any critical condition is detected.
        """
        logger.info(f"SOS check: weather_risk={weather_risk}, health_score={health_score}")

        alert_triggered = False
        alert_types = []
        actions_taken = []

        # Condition 1: High weather risk
        if weather_risk == "High":
            alert_triggered = True
            alert_types.append("High Weather Risk")
            actions_taken.append("Fleet manager notified of hazardous weather conditions.")

        # Condition 2: Critical vehicle health
        if health_score < 50:
            alert_triggered = True
            alert_types.append("Critical Vehicle Health")
            actions_taken.append("Fleet manager notified of vehicle below safety threshold.")

        # Condition 3: Both conditions simultaneously (CRITICAL)
        severity = "Normal"
        if len(alert_types) >= 2:
            severity = "CRITICAL"
        elif len(alert_types) == 1:
            severity = "WARNING"

        if alert_triggered:
            try:
                from backend.app.core.config import settings
                from backend.app.shared.notifications.email import send_email_async

                manager_email = settings.DEMO_DRIVER_EMAIL or "saravanaegs2602@gmail.com"
                subject = f"[AgentFleet] {severity} SOS Alert — Trip {str(trip_id)[:8]}"
                html_body = f"""
                <html>
                  <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width:600px;margin:0 auto;padding:20px;border:2px solid #e11d48;border-radius:8px;">
                      <h2 style="color:#e11d48;">SOS Fleet Alert — {severity}</h2>
                      <p><strong>Trip ID:</strong> {trip_id}</p>
                      <p><strong>Vehicle ID:</strong> {vehicle_id}</p>
                      <p><strong>Alert Types:</strong> {", ".join(alert_types)}</p>
                      <p><strong>Weather Risk:</strong> {weather_risk}</p>
                      <p><strong>Vehicle Health Score:</strong> {health_score} / 100</p>
                      <p style="background:#fff1f2;padding:12px;border-left:4px solid #e11d48;margin-top:15px;">
                        <strong>IMMEDIATE ACTION REQUIRED.</strong> Please review trip status and 
                        contact the driver immediately.
                      </p>
                      <p style="font-size:11px;color:#999;">Automated alert from AgentFleet SOS Agent.</p>
                    </div>
                  </body>
                </html>"""
                text_body = (
                    f"SOS ALERT [{severity}]\nTrip: {trip_id}\nVehicle: {vehicle_id}\n"
                    f"Alerts: {', '.join(alert_types)}\nWeather: {weather_risk}\nHealth: {health_score}/100"
                )
                send_email_async(manager_email, subject, html_body, text_body)
                logger.warning(f"SOS alert email sent to {manager_email}. Types: {alert_types}")
            except Exception as e:
                logger.warning(f"Failed to send SOS alert email: {e}")

        return {
            "alert_triggered": alert_triggered,
            "severity": severity,
            "alert_types": alert_types,
            "actions_taken": actions_taken,
            "weather_risk_input": weather_risk,
            "health_score_input": health_score,
        }
