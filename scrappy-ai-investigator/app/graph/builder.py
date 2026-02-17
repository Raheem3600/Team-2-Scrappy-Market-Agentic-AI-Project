from langgraph.graph import StateGraph, END
from app.graph.state import InvestigationState
from app.graph.nodes import intent_node, planner_node, response_node, select_hypothesis_node, evaluate_node

def route_after_planner(state: InvestigationState):
    if len(state.hypotheses) == 0:
        return "response"
    return "select_hypothesis"

def route_after_evaluation(state):
    CONFIDENCE_THRESHOLD = 0.75

    if state.confidence and state.confidence >= CONFIDENCE_THRESHOLD:
        return "response"

    if state.current_hypothesis_index >= len(state.hypotheses):
        return "response"

    return "select_hypothesis"


def build_graph():
    builder = StateGraph(InvestigationState)

    # Add nodes
    builder.add_node("intent", intent_node)
    builder.add_node("planner", planner_node)
    builder.add_node("select_hypothesis", select_hypothesis_node)
    builder.add_node("evaluate", evaluate_node)
    builder.add_node("response", response_node)

    # Entry
    builder.set_entry_point("intent")

    # Linear start
    builder.add_edge("intent", "planner")

    # Conditional after planner
    builder.add_conditional_edges(
        "planner",
        route_after_planner
    )

    # Hypothesis testing flow
    builder.add_edge("select_hypothesis", "evaluate")

    # Conditional loop
    builder.add_conditional_edges(
        "evaluate",
        route_after_evaluation
    )

    builder.add_edge("response", END)

    return builder.compile()
