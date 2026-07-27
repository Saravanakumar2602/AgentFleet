from backend.app.shared.logger import logger

def query_customer_sms_opt_in(phone: str) -> bool:
    """
    Simulated tool to query opt-in preferences.
    """
    logger.info(f"Checking SMS subscription status for phone: {phone}")
    return True
