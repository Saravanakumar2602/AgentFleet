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

        # 2. Fetch driver user profile
        driver_name = "Driver"
        if trip.get("driver_id"):
            driver = self.repository.get_driver(db, str(trip["driver_id"]))
            if driver and driver.get("name"):
                driver_name = driver["name"]

        # 3. Format estimated duration (ETA)
        minutes = int(trip["estimated_duration"]) if trip.get("estimated_duration") else 0
        hours = minutes // 60
        mins = minutes % 60
        eta_str = f"{hours}h {mins}m"

        # 4. Generate customer alert description
        customer_message = f"Your shipment has been dispatched. Driver {driver_name} is on the way. ETA: {eta_str}."

        # 5. Insert alert record into database notifications table
        # Maps 'Trip Update' to standard DB allowed check constraint 'Dispatch_Notice'
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

        return {
            "trip_id": str(trip["id"]),
            "customer_message": customer_message,
            "notification_type": "Trip Update"
        }
