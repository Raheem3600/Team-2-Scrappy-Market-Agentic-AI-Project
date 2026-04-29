from app.agents.base import BaseAgent


class LineageAgent(BaseAgent):
    name = "LineageAgent"

    def execute(self, state):

        metric = state.intent.metric
        query_type = state.intent.query_type
        entity = state.intent.entity

        # -----------------------------------
        # 2. VIEW SELECTION LOGIC
        # -----------------------------------

        # ✅ DIRECT QUERIES (aggregates)
        if query_type == "direct":
            view = "vw_sales_enriched"

        # ✅ ANALYTICAL (ranking/grouping)
        elif query_type == "analytical":

            if entity and entity.get("type") == "store":
                view = "vw_sales_daily_store"

            elif entity and entity.get("type") == "region":
                view = "vw_sales_daily_store"

            elif state.intent.product or "product" in state.question.lower():
                view = "vw_sales_daily_product"

            else:
                view = "vw_sales_daily_store"  # fallback

        # ✅ INVESTIGATIVE
        else:
            view = "vw_sales_daily_store"

        # -----------------------------------
        # 1. METRIC → COLUMN MAPPING
        # -----------------------------------
        if view == "vw_sales_daily_product":
            if metric == "units_sold":
                metric_column = "UnitsSold"
            else:
                metric_column = "SalesAmount"

        elif view == "vw_sales_daily_store":
            if metric == "units_sold":
                metric_column = "UnitsSold"
            else:
                metric_column = "SalesAmount"

        else:
            if metric == "units_sold":
                metric_column = "UnitsSold"
            else:
                metric_column = "SalesAmount"
        

        # -----------------------------------
        # 3. BUILD CONTEXT
        # -----------------------------------
        state.current_data_context = {
            "view": view,
            "metric_column": metric_column
        }

        print(f"[LineageAgent] Context: {state.current_data_context}")

        return state