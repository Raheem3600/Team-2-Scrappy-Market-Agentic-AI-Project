from app.agents.base import BaseAgent
from app.config.llm import get_llm


class ResponseAgent(BaseAgent):
    name = "ResponseAgent"

    def __init__(self):
        self.llm = get_llm()

    def execute(self, state):

        data = state.evidence[-1].raw_data if state.evidence else []
        if state.intent.query_type == "investigative" and state.confidence < 0.5:
            state.final_answer = (
                f"Low confidence ({state.confidence:.2f}). "
                "Insufficient evidence to determine the root cause."
            )
            state.status = "completed"
            return state

        # ==============================
        # ❌ NO DATA
        # ==============================
        print(state.intent.query_type)
        if not data:
            if state.intent.query_type == "casual":
                state.final_answer = "Hello! How can I assist you today?"
            else:
                state.final_answer = "No data available"
            state.status = "completed"
            return state
        
        limit = state.intent.filters.get("limit", 1)

        # promotion impact comparison
        if state.intent.comparison == "promotion_impact":

            data = state.evidence[-1].raw_data if state.evidence else []

            if len(data) < 2:
                state.final_answer = "Not enough data to compare promotions."
                state.status = "completed"
                return state

            promo_sales = None
            non_promo_sales = None

            for row in data:
                if row.get("WasOnPromotion") in [True, 1]:
                    promo_sales = (
                        row.get("TotalSalesAmount")
                        or row.get("TotalUnitsSold")
                        or row.get("SalesAmount")
                        or row.get("UnitsSold")
                        or row.get("value")
                    )

                else:
                    non_promo_sales = (
                        row.get("TotalSalesAmount")
                        or row.get("TotalUnitsSold")
                        or row.get("SalesAmount")
                        or row.get("UnitsSold")
                        or row.get("value")
                    )

            if promo_sales is None or non_promo_sales is None:
                state.final_answer = "Promotion comparison data incomplete."
                state.status = "completed"
                return state

            lift = round(
                ((promo_sales - non_promo_sales) / non_promo_sales) * 100,
                2
            )

            if lift > 0:
                state.final_answer = (
                    f"Yes. Promotions increased sales by {lift}% "
                    f"({promo_sales} vs {non_promo_sales})."
                )
            else:
                state.final_answer = (
                    f"No. Promotions reduced sales by {abs(lift)}% "
                    f"({promo_sales} vs {non_promo_sales})."
                )

            state.status = "completed"
            return state

        if state.intent.query_type == "analytical" and limit > 1:
            lines = []

            for idx, row in enumerate(data, start=1):

                value = (
                    row.get("value")
                    or row.get("SalesAmount")
                    or row.get("TotalSalesAmount")
                    or row.get("UnitsSold")
                )

                entity = self._format_analytical_entity(row)

                lines.append(f"{idx}. {entity} → {value}")

            state.final_answer = (
                f"Top {limit} results by {state.intent.metric}:\n\n" +
                "\n".join(lines)
            )

            state.status = "completed"
            return state
        
        row = data[0]

        # ==============================
        #  SAFE VALUE EXTRACTION
        # ==============================
        value = (
            row.get("value")
            or row.get("SalesAmount")
            or row.get("TotalSalesAmount")
            or row.get("UnitsSold")
            or row.get("TotalUnitsSold")
        )

        # Convert string → float if needed
        if isinstance(value, str):
            try:
                value = float(value)
            except:
                pass

        # fallback: pick first numeric
        if value is None:
            for v in row.values():
                try:
                    value = float(v)
                    break
                except:
                    continue

        # ==============================
        # 🟢 DIRECT QUERY
        # ==============================
        if state.intent.query_type == "direct":
            state.final_answer = f"Total {state.intent.metric} = {value}"
            state.status = "completed"
            return state

        # ==============================
        # 🔵 ANALYTICAL QUERY
        # ==============================
        if state.intent.query_type == "analytical":
            entity = self._format_analytical_entity(row)
            comparison = self._detect_analytical_comparison(state)

            if comparison in ["lowest", "least", "worst"]:
                state.final_answer = f"{entity} has the lowest {state.intent.metric}: {value}"
            else:
                state.final_answer = f"{entity} has the highest {state.intent.metric}: {value}"

            state.status = "completed"
            return state

        # ==============================
        # 🔴 INVESTIGATIVE → LLM
        # ==============================
        system_prompt = """
        You are a senior retail data analyst.

        Your job is to answer business questions using ONLY the provided data.

        ---

        ## STRICT RULES:

        * NEVER hallucinate numbers
        * NEVER assume trends without evidence
        * If data is empty → respond EXACTLY: "No data available" if its not a casual query
        * ALWAYS use actual values from data
        * DO NOT mention SQL, tables, JSON, APIs, or technical details
        * Be precise, concise, and business-focused
        * respond to casual query based upon the question asked.

        ---

        ## STEP 1: DETERMINE QUESTION TYPE

        Use the question to classify:

        1. DIRECT → "how many", "total", "sum", "count"
        2. ANALYTICAL → "highest", "lowest", "top", "best", "worst"
        3. INVESTIGATIVE → "why", "reason", "underperform", "drop"
        4. CASUAL -> "hi", "hey", "how are you", "what's up", "hello"

        ---

        ## STEP 2: RESPONSE RULES

        🔹 1. DIRECT QUESTIONS

        Return ONLY the number.

        Format:
        Total <metric> = <value>

        Example:
        Total net_sales = 125000

        🔹 2. ANALYTICAL QUESTIONS

        Use ranking from data.

        Rules:

        * Identify entity (store / region / product)
        * Return ONLY top result unless specified
        * DO NOT explain

        Formats:

        For highest: <entity> <id/name> has the highest <metric>: <value>

        For lowest: <entity> <id/name> has the lowest <metric>: <value>

        For top N:
        Top <N> <entities> by <metric>:

        1. <entity> → <value>
        2. <entity> → <value>

        🔹 3. INVESTIGATIVE QUESTIONS

        Structure strictly:

        1. Observation (what is happening)
        2. Evidence (numbers)
        3. Interpretation (ONLY if supported)

        Format: <Observation>. The data shows <evidence>. This indicates <reason>.

        ---

        ## IMPORTANT EDGE RULES

        * If only ONE row exists → still answer normally
        * If values are strings → treat them as numbers
        * If multiple metrics exist → use the most relevant one
        * Prefer SalesAmount for sales, UnitsSold for units

        ---

        ## EXAMPLES

        Input:
        Data: [{"value": 125000}]
        Question: How many sales in 2025?

        Output:
        Total net_sales = 125000

        ---

        Input:
        Data: [{"StoreID": 3, "value": 12450}]
        Question: Which store has the lowest sales?

        Output:
        Store 3 has the lowest net_sales: 12450

        ---

        Input:
        Data: [
        {"StoreID": 1, "value": 90000},
        {"StoreID": 2, "value": 85000},
        {"StoreID": 3, "value": 80000}
        ]
        Question: Top 3 stores by sales

        Output:
        Top 3 stores by net_sales:

        1. Store 1 → 90000
        2. Store 2 → 85000
        3. Store 3 → 80000

        ---

        Input:
        Data: [{"Region": "South", "SalesAmount": 2000}, {"Region": "North", "SalesAmount": 8000}]
        Question: Why are sales low in South?

        Output:
        Sales in the South region are lower than the North. The data shows 2,000 in the South versus 8,000 in the North. This indicates weaker performance in that region.

        ---

        Now answer the question strictly using the rules above.

        """

        prompt = f"""
        {system_prompt}

        User Question:
        {state.question}

        Evidence:
        {data}
        """

        response = self.llm.invoke(prompt)

        state.final_answer = response.content
        state.status = "completed"

        return state

    def _format_analytical_entity(self, row):
        month_name = row.get("MonthName")
        day_name = row.get("DayName")
        quarter = row.get("Quarter")
        year = row.get("Year")
        store = row.get("StoreID")
        region = row.get("Region")
        product = row.get("ProductID")
        category = row.get("Category")

        return (
            f"Month {month_name}" if month_name else
            f"Day {day_name}" if day_name else
            f"Quarter {quarter}" if quarter else
            f"Year {year}" if year else
            f"Store {store}" if store else
            f"Region {region}" if region else
            f"Product {product}" if product else
            f"Category {category}" if category else
            "Result"
        )

    def _detect_analytical_comparison(self, state):
        comparison = state.intent.comparison

        if comparison in {"lowest", "least", "worst"}:
            return "lowest"

        if comparison in {"highest", "top", "best"}:
            return "highest"

        payload = state.current_query.get("payload", {}) if state.current_query else {}
        sort_direction = str(payload.get("sort_direction", "")).upper()

        if sort_direction == "ASC":
            return "lowest"

        if sort_direction == "DESC":
            return "highest"

        question = state.question.lower()

        if any(word in question for word in ["lowest", "least", "worst", "min"]):
            return "lowest"

        if any(word in question for word in ["highest", "top", "best", "most", "max"]):
            return "highest"

        return "highest"
