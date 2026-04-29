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

            filters = state.intent.filters or {}
            question = state.question.lower()

            # promotion impact analysis
            if state.intent.comparison == "promotion_impact":
                view = "vw_sales_enriched"
            
            # explicit store analytics
            elif entity and entity.get("type") == "store":
                view = "vw_sales_daily_store"

            # explicit regional analytics
            elif entity and entity.get("type") == "region":
                view = "vw_sales_daily_store"

            # product analytics
            elif "product" in question:
                # if filtering by region/store/category,
                # use enriched fact view (supports multidimensional filtering)
                if any(
                    key.lower() in {"region", "storeid", "category"}
                    for key in filters.keys()
                ):
                    view = "vw_sales_enriched"
                else:
                    view = "vw_sales_daily_product"

            else:
                view = "vw_sales_daily_store"

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