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
        #  DEFAULT PAYLOAD
        # ==============================

        metric_column = context.get("metric_column", "SalesAmount")

        # fallback safety
        if metric_column not in ["SalesAmount", "UnitsSold"]:
            metric_column = "SalesAmount"

        payload = {
            "view_name": context["view"],
            "metric_column": metric_column,
            "filters": filters
        }

        # ==============================
        #  DIRECT QUERY (SUM)
        # ==============================
        if query_type == "direct":
            payload["aggregation"] = "SUM"

        # ==============================
        #  ANALYTICAL QUERY (GROUP + ORDER)
        # ==============================
        elif query_type == "analytical":

            group_by = self._detect_grouping(state)
            order = self._detect_order(state)

            payload.update({
                "aggregation": "SUM",
                "group_by": group_by,
                "order_by": order,
                "limit": 1
            })

        # ==============================
        # INVESTIGATIVE (SAFE DEFAULT)
        # ==============================
        else:
            payload["limit"] = 50  # avoid huge data 

        print("📡 Query Payload:", payload)

        response = requests.post(
            "http://localhost:8000/query/execute",
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
    #  HELPERS
    # ==============================

    def _build_filters(self, state):
        filters = {}

        raw_filters = state.intent.filters or {}

        for k, v in raw_filters.items():
            if v is not None:
                filters[k] = v

        return filters

    def _get_hypothesis_name(self, state):
        if state.intent.query_type == "direct":
            return "direct_query"

        if state.current_hypothesis_index > 0:
            return state.hypotheses[state.current_hypothesis_index - 1].name

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
