from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger("agentfleet.core.base_agent")

class BaseAgent(ABC):
    """
    Abstract Base Class for all autonomous agents in the AgentFleet system.
    Defines lifecycle hooks for input validation, execution, and output formatting.
    """
    @abstractmethod
    def validate(self, task_data: dict) -> bool:
        """
        Validates the incoming task parameters. Returns True if valid.
        Raises ValueError or exceptions if validation fails.
        """
        pass

    @abstractmethod
    def execute(self, db: Session, task_data: dict) -> dict:
        """
        Executes the concrete service business actions.
        """
        pass

    @abstractmethod
    def format_response(self, result: dict) -> dict:
        """
        Formats raw execution outcomes into standardized outputs.
        """
        pass

    def run(self, db: Session, task_data: dict) -> dict:
        """
        Standard agent execution pipeline executing validation, execution, and formatting.
        """
        logger.info(f"Triggering {self.__class__.__name__} run sequence.")
        self.validate(task_data)
        raw_result = self.execute(db, task_data)
        formatted_result = self.format_response(raw_result)
        logger.info(f"{self.__class__.__name__} run sequence completed successfully.")
        return formatted_result
