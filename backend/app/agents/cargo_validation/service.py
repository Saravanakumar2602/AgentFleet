from sqlalchemy.orm import Session
import logging

logger = logging.getLogger("agentfleet.agents.cargo_validation.service")

MAX_LEGAL_WEIGHT_KG = 40000.0

class CargoValidationService:
    """
    Business layer for Cargo Validation Agent.
    Validates cargo weight against legal limits and classifies hazard level.
    """

    def validate_cargo(self, db: Session, pickup: str, destination: str, cargo_weight: float) -> dict:
        """
        Checks cargo weight against legal transport limits and classifies the cargo.
        """
        logger.info(f"Validating cargo: weight={cargo_weight} kg, {pickup} -> {destination}")

        violations = []
        cargo_class = "Standard"
        is_hazardous = False

        # Legal weight compliance check
        if cargo_weight > MAX_LEGAL_WEIGHT_KG:
            violations.append(f"Cargo weight {cargo_weight} kg exceeds legal maximum of {MAX_LEGAL_WEIGHT_KG} kg.")

        # Cargo classification by weight
        if cargo_weight <= 500:
            cargo_class = "Light Cargo"
        elif cargo_weight <= 5000:
            cargo_class = "Standard Cargo"
        elif cargo_weight <= 20000:
            cargo_class = "Heavy Cargo"
        else:
            cargo_class = "Oversize Cargo"
            if cargo_weight > MAX_LEGAL_WEIGHT_KG:
                is_hazardous = True

        # Weight-based hazard flag (very heavy loads need special permits)
        if cargo_weight > 25000:
            is_hazardous = True

        compliance_status = "Compliant" if not violations else "Non-Compliant"

        if violations:
            logger.warning(f"Cargo validation violations detected: {violations}")
        else:
            logger.info(f"Cargo validation passed: class={cargo_class}, hazardous={is_hazardous}")

        return {
            "cargo_weight_kg": cargo_weight,
            "cargo_class": cargo_class,
            "is_hazardous": is_hazardous,
            "compliance_status": compliance_status,
            "violations": violations,
            "max_legal_weight_kg": MAX_LEGAL_WEIGHT_KG,
        }
