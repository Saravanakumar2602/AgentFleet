from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.supabase import get_db
from backend.app.shared.response import success_response, error_response
from backend.app.shared.logger import logger
from backend.app.agents.customer.schemas import NotificationTriggerRequest

router = APIRouter()

@router.post("/notify", tags=["Customer"])
async def trigger_customer_notification(payload: NotificationTriggerRequest, db: Session = Depends(get_db)):
    """
    Sends out updates regarding ETA revisions or delivery delays to customers.
    """
    logger.info(f"Triggering customer alert for client contact: {payload.customer_contact}")
    try:
        # Placeholder notification result
        result = {
            "customer_contact": payload.customer_contact,
            "channel_used": payload.notification_channel,
            "message_sent": f"Your cargo is in transit. Estimated ETA is 3:30 PM (simulation).",
            "dispatch_status": "sent"
        }
        return success_response(
            data=result, 
            message="Customer notification dispatched successfully (simulation)."
        )
    except Exception as e:
        logger.error(f"Error executing customer agent: {e}")
        return error_response(message="Failed to dispatch customer notification.", error=str(e))
