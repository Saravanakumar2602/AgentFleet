from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.agents.customer.schemas import NotificationRequest

logger = logging.getLogger("agentfleet.agents.customer.routes")
router = APIRouter()

@router.post("/customer/notify", tags=["Customer"])
async def trigger_customer_notification(payload: NotificationRequest, db: Session = Depends(get_db)):
    """
    Exposes POST /customer/notify API.
    Resolves the Customer Communication Agent dynamically from the registry to avoid circular imports.
    """
    # Lazy local import to break circular dependency at package initialization time
    from backend.app.registry.registry import get_agent

    agent = get_agent("customer")
    if not agent:
        logger.error("Customer Communication Agent lookup from registry returned None.")
        raise RuntimeError("Customer Agent not found in Registry.")

    result = agent.run(
        db=db,
        task_data={"trip_id": payload.trip_id}
    )

    # Return formatted run sequence results directly
    return result
