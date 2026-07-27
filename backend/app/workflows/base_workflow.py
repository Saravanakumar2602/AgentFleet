from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger("agentfleet.workflows.base_workflow")

class BaseWorkflow(ABC):
    """
    Abstract Base Class defining the operational hooks for AgentFleet Multi-Agent workflows.
    """
    @abstractmethod
    def validate(self, task_data: dict) -> bool:
        """
        Validates workflow execution inputs. Returns True if valid.
        Raises ValueError or exceptions if validation fails.
        """
        pass

    @abstractmethod
    def execute(self, db: Session, task_data: dict) -> dict:
        """
        Coordinates the step-by-step agent executions.
        """
        pass

    @abstractmethod
    def rollback(self, db: Session, checkpoint_data: dict) -> None:
        """
        Performs database rollbacks or state resets if later stages fail.
        """
        pass

    @abstractmethod
    def format_result(self, steps_data: dict) -> dict:
        """
        Merges step outcomes into a unified success payload.
        """
        pass

    def run(self, db: Session, task_data: dict) -> dict:
        """
        Template method orchestrating validation and execution.
        Handles failures and translates them into standard output dict.
        """
        logger.info(f"Triggering workflow run sequence: {self.__class__.__name__}")
        self.validate(task_data)
        return self.execute(db, task_data)
