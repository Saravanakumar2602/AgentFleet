from backend.app.shared.logger import logger

class CustomerService:
    """
    Business logic layer for Customer Communication Agent.
    """
    def __init__(self):
        pass

    async def draft_eta_notification(self, customer_name: str, delay_minutes: int) -> str:
        logger.info(f"Drafting customer notification for {customer_name} due to delay.")
        if delay_minutes > 0:
            return f"Dear {customer_name}, your delivery is delayed by approximately {delay_minutes} minutes. We apologize for the inconvenience."
        return f"Dear {customer_name}, your delivery is currently on track."
