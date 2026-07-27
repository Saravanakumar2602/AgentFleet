import logging
import sys
from backend.app.core.config import settings

def get_logger(name: str = "agentfleet") -> logging.Logger:
    """
    Configures and returns a custom logger with standardized formats.
    Prevent duplicate handlers when called multiple times.
    """
    logger = logging.getLogger(name)
    
    # Prevent adding handlers multiple times if logger is already configured
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        
        # Standardized log format
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

# Default logger instance
logger = get_logger("agentfleet")
