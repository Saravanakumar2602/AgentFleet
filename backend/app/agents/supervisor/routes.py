from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.agents.supervisor.schemas import SupervisorRequest, SupervisorChatRequest
from backend.app.agents.supervisor.service import SupervisorService

logger = logging.getLogger("agentfleet.agents.supervisor.routes")
router = APIRouter()
supervisor_service = SupervisorService()

@router.post("/supervisor/execute", tags=["Supervisor"])
async def trigger_supervisor_workflow(payload: SupervisorRequest, db: Session = Depends(get_db)):
    """
    Exposes POST /supervisor/execute API.
    Executes the selected multi-agent workflow sequentially and returns timed outcomes.
    """
    result = supervisor_service.execute_workflow(
        db=db,
        workflow_name=payload.workflow,
        pickup=payload.pickup,
        destination=payload.destination,
        weight=payload.weight
    )

    if result.get("status") == "failed":
        logger.warning(f"Supervisor executed workflow with failure result.")
        return JSONResponse(content=result, status_code=400)

    return result

@router.post("/supervisor/chat", tags=["Supervisor"])
async def trigger_supervisor_chat(
    payload: SupervisorChatRequest, 
    db: Session = Depends(get_db)
):
    """
    Exposes POST /supervisor/chat API.
    Orchestrates Groq-driven intent extractions and triggers workflow runs.
    """
    from backend.app.shared.exceptions import AIParserException
    try:
        result = supervisor_service.chat_workflow(
            db=db,
            message=payload.message
        )
        if result.get("status") == "failed":
            return JSONResponse(content=result, status_code=400)
        return result
    except AIParserException as err:
        logger.warning(f"Supervisor natural language parse failed: {err}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "failed",
                "message": "Unable to understand request."
            }
        )

