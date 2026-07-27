from backend.app.shared.logger import logger

def send_external_sms(phone_number: str, message: str) -> bool:
    """
    Simulated tool to call external SMS gateway API.
    """
    logger.info(f"Dispatching SMS to {phone_number}: '{message}'")
    return True

def send_external_email(email_address: str, subject: str, body: str) -> bool:
    """
    Simulated tool to call external Email relay client.
    """
    logger.info(f"Dispatching Email to {email_address} with subject '{subject}'")
    return True
