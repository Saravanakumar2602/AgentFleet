from sqlalchemy.orm import Session
import logging
import urllib.request
import json

logger = logging.getLogger("agentfleet.agents.weather.service")

WEATHER_RISK_THRESHOLDS = {
    "wind_high_kmh": 60,
    "wind_medium_kmh": 30,
}

HAZARDOUS_CONDITIONS = [
    "thunderstorm", "blizzard", "tornado", "hurricane",
    "heavy rain", "heavy snow", "fog", "hail", "sleet"
]


class WeatherService:
    """
    Business layer for Weather Agent.
    Fetches live weather from wttr.in (free, no API key required).
    Falls back gracefully if no internet connection.
    """

    def get_weather(self, db: Session, destination: str) -> dict:
        """
        Fetches weather conditions at destination and assesses route risk.
        """
        logger.info(f"Fetching weather for destination: {destination}")

        # Extract city name from coord string if needed (e.g. "13.08,80.27" -> use coords)
        location = destination.strip()

        try:
            url = f"http://wttr.in/{urllib.parse.quote(location)}?format=j1"
            import urllib.parse
            url = f"http://wttr.in/{urllib.parse.quote(location)}?format=j1"
            req = urllib.request.Request(url, headers={"User-Agent": "AgentFleet/1.0"})
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode())

            current = data["current_condition"][0]
            condition = current["weatherDesc"][0]["value"]
            temp_c = int(current["temp_C"])
            wind_kmh = int(current["windspeedKmph"])
            humidity = int(current["humidity"])
            feels_like = int(current["FeelsLikeC"])

            # Risk assessment
            weather_risk = "Low"
            risk_reasons = []

            if wind_kmh >= WEATHER_RISK_THRESHOLDS["wind_high_kmh"]:
                weather_risk = "High"
                risk_reasons.append(f"Wind speed {wind_kmh} km/h — dangerous for heavy vehicles.")
            elif wind_kmh >= WEATHER_RISK_THRESHOLDS["wind_medium_kmh"]:
                if weather_risk != "High":
                    weather_risk = "Medium"
                risk_reasons.append(f"Moderate wind speed {wind_kmh} km/h.")

            condition_lower = condition.lower()
            for hazard in HAZARDOUS_CONDITIONS:
                if hazard in condition_lower:
                    weather_risk = "High"
                    risk_reasons.append(f"Hazardous condition detected: {condition}.")
                    break

            # Weather delay estimate (minutes)
            weather_delay_minutes = 0
            if weather_risk == "High":
                weather_delay_minutes = 45
            elif weather_risk == "Medium":
                weather_delay_minutes = 20

            logger.info(f"Weather fetched: {condition}, {temp_c}C, wind={wind_kmh}km/h, risk={weather_risk}")

            return {
                "location": location,
                "condition": condition,
                "temperature_c": temp_c,
                "feels_like_c": feels_like,
                "wind_kmh": wind_kmh,
                "humidity_pct": humidity,
                "weather_risk": weather_risk,
                "risk_reasons": risk_reasons,
                "weather_delay_minutes": weather_delay_minutes,
                "source": "wttr.in",
            }

        except Exception as e:
            logger.warning(f"Weather fetch failed ({e}). Using fallback safe conditions.")
            return {
                "location": location,
                "condition": "Clear",
                "temperature_c": 28,
                "feels_like_c": 30,
                "wind_kmh": 12,
                "humidity_pct": 55,
                "weather_risk": "Low",
                "risk_reasons": [],
                "weather_delay_minutes": 0,
                "source": "fallback",
            }
