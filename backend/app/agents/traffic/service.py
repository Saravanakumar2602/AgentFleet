from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger("agentfleet.agents.traffic.service")

class TrafficService:
    """
    Business layer for Traffic Analysis Agent.
    Estimates traffic delay based on time-of-day and day-of-week patterns.
    No external API required — uses deterministic formula.
    """

    def analyze_traffic(self, db: Session, pickup: str, destination: str) -> dict:
        """
        Computes traffic level and estimated delay in minutes.
        Peak hours: 8–10 AM and 5–7 PM on weekdays.
        """
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        is_weekend = weekday >= 5

        logger.info(f"Analyzing traffic conditions at hour={hour}, weekday={weekday}")

        traffic_level = "Low"
        delay_minutes = 0
        congestion_factor = 1.0

        if is_weekend:
            traffic_level = "Low"
            delay_minutes = 5
            congestion_factor = 1.05
        elif 8 <= hour < 10:
            # Morning peak
            traffic_level = "Heavy"
            delay_minutes = 35
            congestion_factor = 1.4
        elif 17 <= hour < 19:
            # Evening peak
            traffic_level = "Heavy"
            delay_minutes = 40
            congestion_factor = 1.45
        elif 10 <= hour < 17:
            # Mid-day moderate
            traffic_level = "Moderate"
            delay_minutes = 15
            congestion_factor = 1.2
        elif 19 <= hour < 22:
            # Early evening
            traffic_level = "Moderate"
            delay_minutes = 10
            congestion_factor = 1.1
        else:
            # Night / early morning
            traffic_level = "Low"
            delay_minutes = 5
            congestion_factor = 1.05

        # Recommend departure window
        if traffic_level == "Heavy":
            recommended_departure = "Depart before 7:30 AM or after 7:30 PM for optimal conditions."
        elif traffic_level == "Moderate":
            recommended_departure = "Current conditions are acceptable. Proceed as planned."
        else:
            recommended_departure = "Ideal travel window. Minimal traffic expected."

        logger.info(f"Traffic result: level={traffic_level}, delay={delay_minutes} min")

        return {
            "traffic_level": traffic_level,
            "delay_minutes": delay_minutes,
            "congestion_factor": congestion_factor,
            "recommended_departure": recommended_departure,
            "analysis_time": now.strftime("%H:%M"),
        }
