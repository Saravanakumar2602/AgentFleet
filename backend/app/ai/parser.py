import re
import logging
from backend.app.ai.intent import FleetIntent

logger = logging.getLogger("agentfleet.ai.parser")

class IntentParser:
    """
    Parser interface and rule-based classifier matching natural language queries 
    to FleetIntent keys and extracting parameters.
    """
    @staticmethod
    def parse(text: str) -> dict:
        """
        Parses text and returns a structured dictionary containing 'intent' and 'parameters'.
        """
        logger.info(f"Parsing natural language input: '{text}'")
        raw_text = text.lower().strip()

        # 1. Classify Intent based on keyword checks
        if "delivery" in raw_text or "workflow" in raw_text:
            intent = FleetIntent.WORKFLOW
        elif "dispatch" in raw_text or "assign" in raw_text:
            intent = FleetIntent.DISPATCH
        elif "route" in raw_text or "path" in raw_text:
            intent = FleetIntent.ROUTE
        elif "maintenance" in raw_text or "health" in raw_text:
            intent = FleetIntent.MAINTENANCE
        elif "analytics" in raw_text or "utilization" in raw_text or "report" in raw_text:
            intent = FleetIntent.ANALYTICS
        elif "notify" in raw_text or "customer" in raw_text or "message" in raw_text:
            intent = FleetIntent.CUSTOMER
        else:
            intent = FleetIntent.UNKNOWN

        # 2. Extract parameters using simple regular expressions
        parameters = {}

        # Extract cargo weight numbers (e.g. '2500 kg', 'weight 500.5', 'capacity of 4500')
        weight_match = re.search(r'(?:weight|capacity|cargo)\s*(?:of|with)?\s*[:=]?\s*(\d+(?:\.\d+)?)', raw_text)
        if weight_match:
            parameters["weight"] = float(weight_match.group(1))

        # Extract vehicle or driver UUIDs
        uuid_matches = re.findall(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', raw_text)
        if uuid_matches:
            parameters["uuids"] = uuid_matches
            if len(uuid_matches) == 1:
                parameters["target_id"] = uuid_matches[0]

        # Extract coordinates templates (e.g., '13.0827,80.2707')
        coord_matches = re.findall(r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)', raw_text)
        if coord_matches:
            parameters["coordinates"] = [f"{lat},{lon}" for lat, lon in coord_matches]

        logger.info(f"Parsed intent: {intent}. Extracted parameters: {parameters}")
        return {
            "intent": intent,
            "parameters": parameters
        }
