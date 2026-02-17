from app.graph.state import InvestigationState, IntentModel, HypothesisModel, InvestigationStatus

def intent_node(state: InvestigationState):
    state.intent = IntentModel(
        metric="net_sales",
        time_range="last_7_days",
        comparison="previous_7_days",
        filters={}
    )
    state.status = "in_progress"
    state.update_timestamp()
    return state

def planner_node(state: InvestigationState):
    state.add_hypothesis(
        HypothesisModel(name="traffic_drop", priority=1)
    )
    state.add_hypothesis(
        HypothesisModel(name="inventory_issue", priority=2)
    )
    return state

def response_node(state: InvestigationState):
    state.status = InvestigationStatus.COMPLETED
    state.update_timestamp()
    return state

def select_hypothesis_node(state):
    if state.current_hypothesis_index >= len(state.hypotheses):
        return state  # No more hypotheses

    current = state.hypotheses[state.current_hypothesis_index]
    current.tested = True
    state.update_timestamp()
    return state

def evaluate_node(state):
    current = state.hypotheses[state.current_hypothesis_index]
    current.score = 0.6

    state.confidence = 0.6

    # Move index forward HERE (safe)
    state.current_hypothesis_index += 1

    state.update_timestamp()
    return state
