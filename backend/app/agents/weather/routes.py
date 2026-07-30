from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from backend.app.database.supabase import get_db
from backend.app.shared.response import build_success_response
from backend.app.agents.weather.schemas import WeatherRequest
from backend.app.agents.weather.service import WeatherService
service = WeatherService()

logger = logging.getLogger("agentfleet.agents.weather.routes")
router = APIRouter()

@router.post("/weather/check", tags=["Weather"])
async def weather_endpoint(p: WeatherRequest, db: Session = Depends(get_db)):
    """
    Fetch weather conditions at destination
    """
    result = service.get_weather(db=db, destination=p.destination)
    return build_success_response(data=result)

