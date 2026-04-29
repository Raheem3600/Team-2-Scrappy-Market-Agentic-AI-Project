from app.agents.base import BaseAgent
from app.graph.state import HypothesisModel
from app.domain.hypotheses import HYPOTHESIS_REGISTRY


class PlannerAgent(BaseAgent):
    name = "PlannerAgent"

    def execute(self, state):

        # 🔥 Skip for direct queries
        if state.intent.query_type == "direct":
            state.hypotheses = []
            return state

        metric = state.intent.metric

        if metric not in HYPOTHESIS_REGISTRY:
            state.hypotheses = []
            return state

        state.hypotheses = []

        for h in HYPOTHESIS_REGISTRY[metric]:
            state.add_hypothesis(
                HypothesisModel(
                    name=h["name"],
                    priority=h["priority"],
                    description=h["description"]
                )
            )

        state.hypotheses = sorted(state.hypotheses, key=lambda x: x.priority)
        state.current_hypothesis_index = 0

        print(f"[PlannerAgent] Generated hypotheses: {[h.name for h in state.hypotheses]}")

        return state