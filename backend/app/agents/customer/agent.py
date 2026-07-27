from sqlalchemy.orm import Session
import logging

from backend.app.core.base_agent import BaseAgent
from backend.app.agents.customer.service import CustomerService

logger = logging.getLogger("agentfleet.agents.customer.agent")

class CustomerAgent(BaseAgent):
    """
    Interface layer for the Customer Communication Agent.
    Inherits from BaseAgent to participate in multi-agent registries.
    """
    def __init__(self, service: CustomerService = CustomerService()):
        self.service = service
        logger.info("CustomerAgent initialized.")

    def validate(self, task_data: dict) -> bool:
        trip_id = task_data.get("trip_id")

        if not trip_id:
            raise ValueError("Invalid execution inputs. 'trip_id' is required.")
        return True

    def execute(self, db: Session, task_data: dict) -> dict:
        trip_id = task_data.get("trip_id")

        return self.service.notify_customer(
            db=db,
            trip_id=trip_id
        )

    def format_response(self, result: dict) -> dict:
        return {
            "status": "success",
            "agent": "Customer Agent",
            "trip_id": result["trip_id"],
            "customer_message": result["customer_message"],
            "notification_type": result["notification_type"]
        }
