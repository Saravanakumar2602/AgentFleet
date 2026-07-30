from sqlalchemy.orm import Session
import logging

logger = logging.getLogger("agentfleet.agents.eta_updater.service")


class EtaUpdaterService:
    """
    Business layer for ETA Updater Agent.
    Combines base route ETA with traffic and weather delays to produce an adjusted final ETA.
    """

    def update_eta(
        self,
        db: Session,
        base_duration_minutes: int,
        traffic_delay_minutes: int,
        weather_delay_minutes: int,
    ) -> dict:
        """
        Computes an adjusted ETA by summing all delay factors on top of the base route duration.
        """
        logger.info(
            f"Updating ETA: base={base_duration_minutes}m, "
            f"traffic_delay={traffic_delay_minutes}m, weather_delay={weather_delay_minutes}m"
        )

        total_delay = traffic_delay_minutes + weather_delay_minutes
        adjusted_total = base_duration_minutes + total_delay

        def fmt(minutes: int) -> str:
            h = minutes // 60
            m = minutes % 60
            if h > 0:
                return f"{h}h {m}m"
            return f"{m}m"

        original_eta_str = fmt(base_duration_minutes)
        adjusted_eta_str = fmt(adjusted_total)

        delay_pct = round((total_delay / base_duration_minutes) * 100, 1) if base_duration_minutes > 0 else 0.0

        logger.info(f"ETA updated: {original_eta_str} -> {adjusted_eta_str} (+{total_delay} min, +{delay_pct}%)")

        return {
            "base_duration_minutes": base_duration_minutes,
            "traffic_delay_minutes": traffic_delay_minutes,
            "weather_delay_minutes": weather_delay_minutes,
            "total_delay_minutes": total_delay,
            "original_eta": original_eta_str,
            "adjusted_eta": adjusted_eta_str,
            "delay_percentage": delay_pct,
        }
