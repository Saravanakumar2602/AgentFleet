from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.agents.analytics.schemas import AnalyticsRequest
from backend.app.agents.analytics.service import AnalyticsService
from backend.app.shared.response import build_success_response

logger = logging.getLogger("agentfleet.agents.analytics.routes")
router = APIRouter()
analytics_service = AnalyticsService()

@router.post("/analytics/report", tags=["Analytics"])
async def generate_fleet_report(payload: AnalyticsRequest, db: Session = Depends(get_db)):
    """
    Exposes POST /analytics/report API. Computes trip distances, fuel ratings,
    inspections counters, and outputs formatted recommendations.
    """
    result = analytics_service.generate_report(
        db=db,
        vehicle_id=payload.vehicle_id
    )

    return build_success_response(
        data={
            "agent": "Fleet Analytics Agent",
            "vehicle": result["vehicle"],
            "total_trips": result["total_trips"],
            "average_distance": result["average_distance"],
            "fuel_efficiency": result["fuel_efficiency"],
            "maintenance_count": result["maintenance_count"],
            "utilization": result["utilization"],
            "recommendation": result["recommendation"]
        },
        message="Analytics report generated successfully."
    )
