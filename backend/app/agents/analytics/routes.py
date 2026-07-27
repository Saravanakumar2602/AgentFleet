from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.supabase import get_db
from backend.app.shared.response import success_response, error_response
from backend.app.shared.logger import logger
from backend.app.agents.analytics.schemas import AnalyticsReportRequest

router = APIRouter()

@router.post("/report", tags=["Analytics"])
async def trigger_analytics_report(payload: AnalyticsReportRequest, db: Session = Depends(get_db)):
    """
    Triggers the generation of fleet utilization metrics and reports.
    """
    logger.info(f"Received analytics request for timeframe of {payload.days_range} days.")
    try:
        # Placeholder analytics results
        result = {
            "days_range": payload.days_range,
            "fleet_utilization_rate": 0.84,
            "total_trips_completed": 1240,
            "deadhead_miles_percentage": 0.11,
            "cost_savings_estimate_usd": 4200.00
        }
        return success_response(
            data=result, 
            message="Fleet analytics report compiled successfully (simulation)."
        )
    except Exception as e:
        logger.error(f"Error executing analytics agent: {e}")
        return error_response(message="Failed to generate analytics report.", error=str(e))
