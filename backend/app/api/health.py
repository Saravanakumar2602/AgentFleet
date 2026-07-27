from fastapi import APIRouter
from fastapi.responses import JSONResponse
import logging

from backend.app.database.supabase import health_check

logger = logging.getLogger("agentfleet.api.health")
router = APIRouter()

@router.get("/database", tags=["Health"])
async def check_database_health():
    """
    Checks connection to the Supabase database.
    """
    try:
        health_check()
        return {
            "status": "connected",
            "database": "supabase"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "failed",
                "message": "Database unavailable"
            }
        )
