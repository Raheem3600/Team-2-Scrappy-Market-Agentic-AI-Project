from app.agents.base import BaseAgent
from app.graph.state import InvestigationStatus


class ResponseAgent(BaseAgent):
    name = "ResponseAgent"

    def execute(self, state):
        state.status = InvestigationStatus.COMPLETED
        state.confidence = 0.8
        state.update_timestamp()
        return state
