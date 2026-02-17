from langgraph.graph import StateGraph, END
from app.graph.state import InvestigationState
from app.graph.nodes import intent_node, planner_node, response_node


def build_graph():
    builder = StateGraph(InvestigationState)

    builder.add_node("intent", intent_node)
    builder.add_node("planner", planner_node)
    builder.add_node("response", response_node)

    builder.set_entry_point("intent")

    builder.add_edge("intent", "planner")
    builder.add_edge("planner", "response")
    builder.add_edge("response", END)

    return builder.compile()
