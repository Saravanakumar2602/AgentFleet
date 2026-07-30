from sqlalchemy.orm import Session
import logging

from backend.app.agents.customer.repository import CustomerRepository
from backend.app.shared.exceptions import AgentFleetException

logger = logging.getLogger("agentfleet.agents.customer.service")

class CustomerService:
    """
    Business layer for Customer Communication Agent.
    Coordinates customer alert text formatting and database notifications logging.
    """
    def __init__(self, repository: CustomerRepository = CustomerRepository()):
        self.repository = repository

    def notify_customer(self, db: Session, trip_id: str) -> dict:
        """
        Loads trip attributes, constructs ETA tracking descriptions,
        saves alerts in notifications logs, and returns details.
        """
        logger.info(f"Generating customer notification for trip: {trip_id}")

        # 1. Fetch trip details
        trip = self.repository.get_trip(db, trip_id)
        if not trip:
            logger.warning(f"Trip not found in database: {trip_id}")
            raise AgentFleetException("Trip not found.", status_code=400)

        # 2. Fetch driver & vehicle details
        driver_name = "Driver"
        driver_phone = "N/A"
        if trip.get("driver_id"):
            driver = self.repository.get_driver(db, str(trip["driver_id"]))
            if driver:
                if driver.get("name"):
                    driver_name = driver["name"]
                if driver.get("phone"):
                    driver_phone = driver["phone"]

        vehicle_num = "Vehicle"
        if trip.get("vehicle_id"):
            veh = self.repository.get_vehicle(db, str(trip["vehicle_id"]))
            if veh and veh.get("vehicle_number"):
                vehicle_num = veh["vehicle_number"]

        # 3. Format estimated duration (ETA)
        minutes = int(trip["estimated_duration"]) if trip.get("estimated_duration") else 0
        hours = minutes // 60
        mins = minutes % 60
        eta_str = f"{hours}h {mins}m"

        # 4. Generate customer alert description
        customer_message = f"Your shipment has been dispatched. Driver {driver_name} is on the way. ETA: {eta_str}."

        # 5. Insert alert record into database notifications table
        try:
            self.repository.insert_notification(
                db=db,
                trip_id=str(trip["id"]),
                message=customer_message,
                notification_type="Dispatch_Notice"
            )
            logger.info(f"Customer alert log successfully recorded for trip: {trip_id}")
        except Exception as e:
            logger.error(f"Failed to record customer notification log: {e}")
            raise e

        # Outbound Email Notification to the Customer
        try:
            from backend.app.core.config import settings
            from backend.app.shared.notifications.email import send_email_async
            
            customer_email = settings.DEMO_CUSTOMER_EMAIL
            if customer_email:
                pickup = trip["source"]
                destination = trip["destination"]
                gmaps_url = f"https://www.google.com/maps/dir/?api=1&origin={pickup}&destination={destination}"
                
                subject = f"[AgentFleet] Shipment Dispatch Confirmation (Trip ID: {str(trip['id'])[:8]})"
                html_body = f"""
                <html>
                  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                      <h2 style="color: #10b981; border-bottom: 2px solid #10b981; padding-bottom: 10px;">Shipment Dispatched Confirmation</h2>
                      <p>Dear Customer,</p>
                      <p>We are pleased to inform you that your shipment has been successfully dispatched and is currently in transit.</p>
                      
                      <h4 style="margin-bottom: 5px; color: #111;">Trip Details:</h4>
                      <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        <tr>
                          <td style="padding: 6px; border-bottom: 1px solid #eee; font-weight: bold; width: 150px;">Origin:</td>
                          <td style="padding: 6px; border-bottom: 1px solid #eee;">{pickup}</td>
                        </tr>
                        <tr>
                          <td style="padding: 6px; border-bottom: 1px solid #eee; font-weight: bold;">Destination:</td>
                          <td style="padding: 6px; border-bottom: 1px solid #eee;">{destination}</td>
                        </tr>
                        <tr>
                          <td style="padding: 6px; border-bottom: 1px solid #eee; font-weight: bold;">Route Distance:</td>
                          <td style="padding: 6px; border-bottom: 1px solid #eee;">{trip.get('distance_km', 0.0)} km</td>
                        </tr>
                        <tr>
                          <td style="padding: 6px; border-bottom: 1px solid #eee; font-weight: bold;">Estimated Time (ETA):</td>
                          <td style="padding: 6px; border-bottom: 1px solid #eee; color: #10b981; font-weight: bold;">{eta_str}</td>
                        </tr>
                      </table>

                      <h4 style="margin-bottom: 5px; color: #111;">Driver & Vehicle Details:</h4>
                      <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        <tr>
                          <td style="padding: 6px; border-bottom: 1px solid #eee; font-weight: bold; width: 150px;">Driver Name:</td>
                          <td style="padding: 6px; border-bottom: 1px solid #eee;">{driver_name}</td>
                        </tr>
                        <tr>
                          <td style="padding: 6px; border-bottom: 1px solid #eee; font-weight: bold;">Driver Phone:</td>
                          <td style="padding: 6px; border-bottom: 1px solid #eee;">{driver_phone}</td>
                        </tr>
                        <tr>
                          <td style="padding: 6px; border-bottom: 1px solid #eee; font-weight: bold;">Vehicle Plate:</td>
                          <td style="padding: 6px; border-bottom: 1px solid #eee;">{vehicle_num}</td>
                        </tr>
                      </table>

                      <div style="margin: 25px 0; text-align: center;">
                        <a href="{gmaps_url}" target="_blank" 
                           style="background-color: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                           Track Delivery Route on Maps
                        </a>
                      </div>
                      
                      <p style="font-size: 12px; color: #666; border-top: 1px solid #eee; padding-top: 15px;">
                        This is a transactional shipment update from the AgentFleet supervisor network.
                      </p>
                    </div>
                  </body>
                </html>
                """
                text_body = f"Dear Customer,\n\nYour shipment has been dispatched!\nDriver: {driver_name}\nPhone: {driver_phone}\nVehicle: {vehicle_num}\nRoute: {pickup} to {destination}\nEstimated ETA: {eta_str}\nTracking Link: {gmaps_url}"
                
                send_email_async(customer_email, subject, html_body, text_body)
        except Exception as email_err:
            logger.warning(f"Failed to dispatch customer shipment email: {email_err}")

        return {
            "trip_id": str(trip["id"]),
            "customer_message": customer_message,
            "notification_type": "Trip Update"
        }
