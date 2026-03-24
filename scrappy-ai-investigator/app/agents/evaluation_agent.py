from app.agents.base import BaseAgent
from app.graph.state import InvestigationState


class EvaluationAgent(BaseAgent):
    name = "EvaluationAgent"   # ✅ set class attribute

    def execute(self, state: InvestigationState):

        current_index = max(state.current_hypothesis_index - 1, 0)

        if current_index >= len(state.hypotheses):
            return state

        hypothesis = state.hypotheses[current_index]

        # Find matching evidence
        evidence = next(
            (e for e in reversed(state.evidence) if e.hypothesis == hypothesis.name),
            None
        )

        if not evidence or not evidence.raw_data:
            score = 0.1
        else:
            row_count = len(evidence.raw_data)

            if row_count > 5:
                score = 0.8
            elif row_count > 2:
                score = 0.6
            else:
                score = 0.3

        hypothesis.score = score
        hypothesis.tested = True

        scores = [h.score for h in state.hypotheses if h.score is not None]
        state.confidence = max(scores) if scores else 0.0

        return state