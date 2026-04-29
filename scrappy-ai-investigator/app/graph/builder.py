from langgraph.graph import StateGraph, END
from app.graph.state import InvestigationState
from app.graph.nodes import intent_node, planner_node, response_node, select_hypothesis_node, evaluate_node
from app.agents.intent_agent import IntentAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.response_agent import ResponseAgent
from app.agents.lineage_agent import LineageAgent
from app.agents.query_agent import QueryBuilderAgent
from app.agents.evaluation_agent import EvaluationAgent

intent_agent = IntentAgent()
planner_agent = PlannerAgent()
response_agent = ResponseAgent()
lineage_agent = LineageAgent()
query_agent = QueryBuilderAgent()
evaluation_agent = EvaluationAgent()

def route_after_planner(state):

    # 🔥 DIRECT → go to query
    # direct → query
    if state.intent.query_type == "direct":
        return "lineage"

    # analytical → query
    if state.intent.query_type == "analytical":
        return "lineage"

    # investigative → hypotheses required
    if len(state.hypotheses) == 0:
        return "response"

    return "select_hypothesis"

def route_after_evaluation(state):

    # direct → done
    if state.intent.query_type == "direct":
        return "response"

    # analytical → done
    if state.intent.query_type == "analytical":
        return "response"

    # investigative → confidence loop
    CONFIDENCE_THRESHOLD = 0.75

    if state.confidence >= CONFIDENCE_THRESHOLD:
        return "response"

    if state.current_hypothesis_index + 1 >= len(state.hypotheses):
        return "response"

    state.current_hypothesis_index += 1
    return "select_hypothesis"

# def route_after_evaluation(state):

#     print("Confidence:", state.confidence)
#     print("Current hypothesis index:", state.current_hypothesis_index)
#     print("Total hypotheses:", len(state.hypotheses))

#     if state.intent.query_type == "direct":
#         print("ROUTE -> response (direct)")
#         return "response"

#     if state.intent.query_type == "analytical":
#         print("ROUTE -> response (analytical)")
#         return "response"

#     CONFIDENCE_THRESHOLD = 0.75

#     if state.confidence and state.confidence >= CONFIDENCE_THRESHOLD:
#         print("ROUTE -> response (confidence met)")
#         return "response"

#     if state.current_hypothesis_index + 1 >= len(state.hypotheses):
#         print("ROUTE -> response (no hypotheses left)")
#         return "response"

#     state.current_hypothesis_index += 1

#     print("ROUTE -> select_hypothesis")
#     print("Next hypothesis index:", state.current_hypothesis_index)

#     return "select_hypothesis"

def route_after_intent(state):
    if state.intent.query_type == "casual":
        return "response"
    return "planner"


def build_graph():
    builder = StateGraph(InvestigationState)

    # Add nodes
    builder.add_node("intent", intent_agent)
    builder.add_node("planner", planner_agent)
    builder.add_node("select_hypothesis", select_hypothesis_node)
    builder.add_node("lineage", lineage_agent)
    builder.add_node("query", query_agent)
    builder.add_node("evaluate", evaluation_agent)
    builder.add_node("response", response_agent)

    # Entry
    builder.set_entry_point("intent")

    # Linear start
    builder.add_conditional_edges(
        "intent",
        route_after_intent
    )

    # Conditional after planner
    builder.add_conditional_edges(
        "planner",
        route_after_planner
    )

    # Hypothesis testing flow
    builder.add_edge("select_hypothesis", "lineage")
    #builder.add_edge("lineage", "evaluate")
    builder.add_edge("lineage", "query")
    builder.add_edge("query", "evaluate")

    # Conditional loop
    builder.add_conditional_edges(
        "evaluate",
        route_after_evaluation
    )

    builder.add_edge("response", END)

    return builder.compile()