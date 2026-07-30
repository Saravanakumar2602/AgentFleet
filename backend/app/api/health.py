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

@router.get("/reset", tags=["Health"])
async def reset_database():
    """
    Clears all active trips and sets all vehicles and drivers to Available.
    """
    from backend.app.database.supabase import SessionLocal
    from sqlalchemy import text
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM trips"))
        db.execute(text("UPDATE vehicles SET status = 'Available'"))
        db.execute(text("UPDATE drivers SET status = 'Available'"))
        db.commit()
        return {
            "status": "success",
            "message": "Database reset successful: Trips cleared. All vehicles and drivers set to 'Available'."
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to reset database: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Database reset failed: {e}"
            }
        )
    finally:
        db.close()
