import os
import requests
from app.agents.base import BaseAgent
from app.graph.state import EvidenceModel


DATA_API_BASE_URL = os.getenv("DATA_API_BASE_URL", "http://localhost:8000/query")
HTTP_SESSION = requests.Session()


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

            state.current_query_dimension = group_by

            analysis_type = "top_n"
            limit = state.intent.filters.get("limit", 1)

            # breakdown queries should return all grouped rows
            if state.intent.comparison == "breakdown":
                analysis_type = "breakdown"
                limit = 100

            payload = {
                "analysis_type": analysis_type,
                "view_name": context["view"],
                "group_by": [group_by],
                "metrics": [metric_column],
                "filters": filters,
                "limit": limit,
                "sort_direction": order
            }

            if state.intent.comparison == "promotion_impact":
                payload = {
                    "analysis_type": "promotion_comparison",
                    "view_name": context["view"],
                    "group_by": ["WasOnPromotion"],
                    "metrics": ["UnitsSold"],
                    "filters": {},
                    "aggregation": "AVG",
                    "limit": 2
                }

        # ==============================
        # 🔴 INVESTIGATIVE (SAFE DEFAULT)
        # ==============================
        else:
            payload["limit"] = 50  # avoid huge data 

        print("📡 Query Payload:", payload)

        endpoint = f"{DATA_API_BASE_URL}/execute"

        if query_type == "analytical":
            endpoint = f"{DATA_API_BASE_URL}/analyze"

        response = HTTP_SESSION.post(
            endpoint,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"API Error: {response.text}")

        result = response.json()

        data = result.get("results", [])
        sql = result.get("sql", "")
        params = result.get("params", [])

        state.current_query = {
            "sql": sql,
            "params": params,
            "payload": payload
        }

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

        column_map = {
            "storeid": "StoreID",
            "region": "Region",
            "productname": "ProductName",
            "category": "Category"
        }

        for k, v in raw_filters.items():
            normalized = column_map.get(k.lower())

            if normalized and v is not None:
                filters[normalized] = v

        return filters

    def _get_hypothesis_name(self, state):
        if state.intent.query_type == "direct":
            return "direct_query"

        if state.hypotheses and state.current_hypothesis_index < len(state.hypotheses):
            return state.hypotheses[state.current_hypothesis_index].name

        return "unknown"

    def _detect_grouping(self, state):

        filters = state.intent.filters or {}
        question = state.question.lower()

        if "month" in question:
            return "MonthName"

        if "quarter" in question:
            return "Quarter"

        if "year" in question:
            return "Year"

        if "day" in question:
            return "DayName"

        # if region is already a filter, don't group by it
        if "region" in filters and "product" in question:
            return "ProductID"

        if "product" in question:
            return "ProductID"

        if "category" in question:
            return "Category"

        if "store" in question:
            return "StoreID"

        if "region" in question:
            return "Region"

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
