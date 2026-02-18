import uuid
from app.graph.builder import build_graph
from app.graph.state import InvestigationState


if __name__ == "__main__":
    graph = build_graph()

    initial_state = InvestigationState(
        investigation_id=str(uuid.uuid4()),
        question="Why are sales down?"
    )

    result = graph.invoke(initial_state)

    result_state = InvestigationState(**result)

    print(result_state.model_dump_json(indent=2))
