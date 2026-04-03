from app.agents.base import BaseAgent


class EvaluationAgent(BaseAgent):
    name = "EvaluationAgent"

    def execute(self, state):

        # DIRECT → no evaluation needed
        if state.intent.query_type == "direct":
            state.confidence = 1.0
            return state

        if not state.hypotheses:
            state.confidence = 0.0
            return state

        current_index = max(state.current_hypothesis_index - 1, 0)

        if current_index >= len(state.hypotheses):
            return state

        hypothesis = state.hypotheses[current_index]

        evidence = next(
            (e for e in reversed(state.evidence) if e.hypothesis == hypothesis.name),
            None
        )

        if not evidence or not evidence.raw_data:
            score = 0.1
        else:
            score = 0.8

        hypothesis.score = score
        hypothesis.tested = True

        state.confidence = max(
            [h.score for h in state.hypotheses if h.score is not None],
            default=0.0
        )

        return state
