from app.agents.base import BaseAgent
from app.graph.state import HypothesisModel


class PlannerAgent(BaseAgent):
    name = "PlannerAgent"

    def execute(self, state):
        state.add_hypothesis(
            HypothesisModel(name="traffic_drop", priority=1)
        )
        state.add_hypothesis(
            HypothesisModel(name="inventory_issue", priority=2)
        )
        return state
