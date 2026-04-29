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

        current_index = state.current_hypothesis_index

        if current_index >= len(state.hypotheses):
            return state

        hypothesis = state.hypotheses[current_index]

        evidence = next(
            (e for e in reversed(state.evidence) if e.hypothesis == hypothesis.name),
            None
        )

        if not evidence or not evidence.raw_data:
            score = 0.0

        else:
            row_count = len(evidence.raw_data)

            # richer scoring
            if row_count == 0:
                score = 0.0
            elif row_count < 3:
                score = 0.4
            elif row_count < 10:
                score = 0.7
            else:
                score = 0.9

        hypothesis.score = score
        hypothesis.tested = True

        state.confidence = max(
            [h.score for h in state.hypotheses if h.score is not None],
            default=0.0
        )

        return state
