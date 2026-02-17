from app.agents.base import BaseAgent
from app.graph.state import IntentModel, InvestigationStatus


class IntentAgent(BaseAgent):
    name = "IntentAgent"

    def execute(self, state):
        state.intent = IntentModel(
            metric="net_sales",
            time_range="last_7_days",
            comparison="previous_7_days",
            filters={}
        )

        state.status = InvestigationStatus.IN_PROGRESS
        state.update_timestamp()
        return state
