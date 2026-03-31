from fastapi import FastAPI
from app.graph.builder import build_graph
from app.graph.state import InvestigationState
import uuid

app = FastAPI()

graph = build_graph()


@app.post("/investigate")
def investigate(payload: dict):
    question = payload.get("question")

    state = InvestigationState(
        investigation_id=str(uuid.uuid4()),
        question=question,
        status="in_progress"
    )

    result = graph.invoke(state)

    print(result)

    return {
        "answer": result["final_answer"],
        "confidence": result["confidence"],
        "hypotheses": [h.model_dump() for h in result["hypotheses"]],
        "evidence": [e.model_dump() for e in result["evidence"]]
    }
