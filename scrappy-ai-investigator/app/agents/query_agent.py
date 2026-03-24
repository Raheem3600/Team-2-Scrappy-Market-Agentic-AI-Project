import requests
from app.agents.base import BaseAgent
from app.graph.state import EvidenceModel


class QueryBuilderAgent(BaseAgent):
    name = "QueryBuilderAgent"

    def execute(self, state):
        context = state.current_data_context

        if not context:
            raise Exception("No data context available")

        # 🔥 Extract filter from intent
        filters = self._build_filters(state)

        payload = {
            "view_name": context["view"],
            "filters": filters,
            "limit": 50
        }

        print("📡 Query Payload:", payload)

        response = requests.post(
            "http://localhost:8000/query/execute",
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"API Error: {response.text}")

        result = response.json()

        if not result.get("success"):
            raise Exception("Query execution failed")

        data = result.get("results", [])

        # 🔥 Attach evidence
        state.add_evidence(
            EvidenceModel(
                hypothesis=state.hypotheses[state.current_hypothesis_index].name,
                summary=f"Fetched {len(data)} rows from {context['view']}",
                raw_data=data[:5]
            )
        )

        return state

    def _build_filters(self, state):
        filters = {}

        # 🔥 Time filter mapping (basic version)
        if state.intent.time_range == "yesterday":
            filters["Date"] = self._get_yesterday()

        # Future:
        # region filter
        # category filter

        return filters

    def _get_yesterday(self):
        from datetime import date, timedelta
        return str(date.today() - timedelta(days=1))