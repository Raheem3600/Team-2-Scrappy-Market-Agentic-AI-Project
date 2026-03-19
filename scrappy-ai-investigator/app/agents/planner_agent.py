from app.agents.base import BaseAgent
from app.graph.state import HypothesisModel
from app.domain.hypotheses import HYPOTHESIS_REGISTRY


class PlannerAgent(BaseAgent):
    name = "PlannerAgent"

    def execute(self, state):
        metric = state.intent.metric

        if metric not in HYPOTHESIS_REGISTRY:
            raise Exception(f"No hypotheses defined for metric: {metric}")

        hypotheses_config = HYPOTHESIS_REGISTRY[metric]

        # Clear old hypotheses (important for re-runs)
        state.hypotheses = []

        for h in hypotheses_config:
            state.add_hypothesis(
                HypothesisModel(
                    name=h["name"],
                    priority=h["priority"],
                    description=h["description"]
                )
            )

        # Sort by priority
        state.hypotheses = sorted(
            state.hypotheses,
            key=lambda x: x.priority
        )

        return state