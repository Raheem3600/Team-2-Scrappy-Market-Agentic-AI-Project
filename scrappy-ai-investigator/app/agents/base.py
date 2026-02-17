from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
import logging

from app.graph.state import InvestigationState

logger = logging.getLogger(__name__)


class AgentExecutionError(Exception):
    pass


class BaseAgent(ABC):
    """
    Base contract for all agents.
    """

    name: str = "base_agent"

    def __call__(self, state: InvestigationState) -> InvestigationState:
        """
        Wrapper that:
        - logs execution
        - catches errors
        - enforces return type
        """
        start_time = datetime.utcnow()
        logger.info(f"[{self.name}] START")

        try:
            updated_state = self.execute(state)

            if not isinstance(updated_state, InvestigationState):
                raise AgentExecutionError(
                    f"{self.name} must return InvestigationState"
                )

            logger.info(f"[{self.name}] SUCCESS")
            return updated_state

        except Exception as e:
            logger.exception(f"[{self.name}] FAILED")
            state.status = "failed"
            raise AgentExecutionError(f"{self.name} failed: {str(e)}") from e

        finally:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"[{self.name}] DURATION: {duration:.3f}s")

    @abstractmethod
    def execute(self, state: InvestigationState) -> InvestigationState:
        """
        Implement actual agent logic here.
        """
        pass
