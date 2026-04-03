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

    # DIRECT / ANALYTICAL → skip loop
    if state.intent.query_type in ["direct", "analytical"]:
        state.confidence = 1.0
        return state

    # INVESTIGATIVE FLOW
    if not state.hypotheses:
        return state

    #  SAFE INDEX
    if state.current_hypothesis_index >= len(state.hypotheses):
        return state

    current = state.hypotheses[state.current_hypothesis_index]

    current.tested = True

    #  MOVE FORWARD
    state.current_hypothesis_index += 1

    return state
