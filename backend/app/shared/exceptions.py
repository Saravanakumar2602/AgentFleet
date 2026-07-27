class AgentFleetException(Exception):
    """
    Base exception class for all AgentFleet application exceptions.
    """
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class VehicleUnavailableException(AgentFleetException):
    """
    Exception raised when no available vehicle matches cargo requirements.
    """
    def __init__(self, message: str = "No suitable vehicle found."):
        super().__init__(message, status_code=400)

class DriverUnavailableException(AgentFleetException):
    """
    Exception raised when no drivers are available for assignment.
    """
    def __init__(self, message: str = "No available driver found."):
        super().__init__(message, status_code=400)

class InvalidCoordinateException(AgentFleetException):
    """
    Exception raised when location coordinate parsing or checks fail.
    """
    def __init__(self, message: str = "Invalid coordinates provided."):
        super().__init__(message, status_code=400)
