import requests
from app.agents.base import BaseAgent
from app.graph.state import EvidenceModel


class QueryBuilderAgent(BaseAgent):
    name = "QueryBuilderAgent"

    def execute(self, state):

        context = state.current_data_context

        if not context:
            print("[QueryBuilderAgent] No data context found")
            raise Exception("No data context") 

        filters = self._build_filters(state)

        query_type = state.intent.query_type

        # ==============================
        # 🔥 DEFAULT PAYLOAD
        # ==============================

        metric_column = context.get("metric_column")

        if not metric_column:
            metric_column = "SalesAmount"

        payload = {
            "view_name": context["view"],
            "metric_column": metric_column,
            "filters": filters
        }

        


        # ==============================
        # 🟢 DIRECT QUERY (SUM)
        # ==============================
        if query_type == "direct":
            payload["aggregation"] = "SUM"

        # ==============================
        # 🔵 ANALYTICAL QUERY (GROUP + ORDER)
        # ==============================
        elif query_type == "analytical":

            group_by = self._detect_grouping(state)
            order = self._detect_order(state)

            payload = {
                "analysis_type": "top_n",
                "view_name": context["view"],
                "group_by": [group_by],     # must be list
                "metrics": [metric_column], # must be list
                "filters": filters,
                "limit": state.intent.filters.get("limit", 1),
                "sort_direction": order
            }

        # ==============================
        # 🔴 INVESTIGATIVE (SAFE DEFAULT)
        # ==============================
        else:
            payload["limit"] = 50  # avoid huge data 

        print("📡 Query Payload:", payload)

        state.current_query = payload.copy()

        endpoint = "http://localhost:8000/query/execute"

        if query_type == "analytical":
            endpoint = "http://localhost:8000/query/analyze"

        response = requests.post(
            endpoint,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"API Error: {response.text}")

        result = response.json()
        data = result.get("results", [])

        state.add_evidence(
            EvidenceModel(
                hypothesis=self._get_hypothesis_name(state),
                summary=f"Fetched {len(data)} rows",
                raw_data=data
            )
        )

        print(f"[QueryBuilderAgent] Retrieved {len(data)} rows")

        return state

    # ==============================
    # 🧠 HELPERS
    # ==============================

    def _build_filters(self, state):
        filters = {}

        raw_filters = state.intent.filters or {}

        allowed_filter_columns = {
            "StoreID",
            "Region",
            "ProductName",
            "Category"
        }

        for k, v in raw_filters.items():
            if k in allowed_filter_columns and v is not None:
                filters[k] = v

        return filters

    def _get_hypothesis_name(self, state):
        if state.intent.query_type == "direct":
            return "direct_query"

        if state.hypotheses and state.current_hypothesis_index < len(state.hypotheses):
            return state.hypotheses[state.current_hypothesis_index].name

        return "unknown"

    def _detect_grouping(self, state):
        """
        Decide GROUP BY column
        """

        question = state.question.lower()

        if "store" in question:
            return "StoreID"

        if "region" in question:
            return "Region"

        if "product" in question:
            return "ProductID"

        if "category" in question:
            return "Category"

        # fallback
        return "StoreID"

    def _detect_order(self, state):
        """
        Decide sorting direction
        """

        question = state.question.lower()

        if any(word in question for word in ["lowest", "least", "worst"]):
            return "ASC"

        if any(word in question for word in ["highest", "top", "best"]):
            return "DESC"

        return "DESC"