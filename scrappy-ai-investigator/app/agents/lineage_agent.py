from app.agents.base import BaseAgent
from app.domain.lineage import LINEAGE_REGISTRY


class LineageAgent(BaseAgent):
    name = "LineageAgent"

    def execute(self, state):
        idx = state.current_hypothesis_index

        if idx >= len(state.hypotheses):
            return state

        hypothesis = state.hypotheses[idx].name

        if hypothesis not in LINEAGE_REGISTRY:
            raise Exception(f"No lineage mapping for {hypothesis}")

        mapping = LINEAGE_REGISTRY[hypothesis]

        state.current_data_context = {
            "view": mapping["view"],
            "group_by": mapping["group_by"],
            "metrics": mapping["metrics"]
        }

        state.update_timestamp()
        return state