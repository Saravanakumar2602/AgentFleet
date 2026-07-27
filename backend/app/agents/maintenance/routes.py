from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.supabase import get_db
from backend.app.shared.response import success_response, error_response
from backend.app.shared.logger import logger
from backend.app.agents.maintenance.schemas import TelemetryReportRequest

router = APIRouter()

@router.post("/telemetry", tags=["Maintenance"])
async def report_telemetry(payload: TelemetryReportRequest, db: Session = Depends(get_db)):
    """
    Submits telemetry data to evaluate vehicle health and trigger alerts.
    """
    logger.info(f"Received telemetry report for vehicle {payload.vehicle_id}")
    try:
        # Placeholder evaluation
        engine_temp = payload.telemetry_data.get("engine_temperature_c", 85.0)
        status = "OK"
        recommendation = "Keep operating."
        
        if engine_temp > 105.0:
            status = "CRITICAL"
            recommendation = "Pull over and schedule cooling system diagnostics immediately."

        result = {
            "vehicle_id": payload.vehicle_id,
            "evaluation_status": status,
            "recommendation": recommendation
        }
        return success_response(
            data=result, 
            message="Vehicle health telemetry parsed successfully (simulation)."
        )
    except Exception as e:
        logger.error(f"Error executing maintenance agent: {e}")
        return error_response(message="Failed to parse telemetry.", error=str(e))
