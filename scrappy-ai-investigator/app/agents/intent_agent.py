from app.agents.base import BaseAgent
from app.graph.state import IntentModel, InvestigationStatus
from app.config.llm import get_llm
from pydantic import ValidationError
from app.domain.metric_mapper import canonicalize_metric
import json
import re


# ----------------------------------------
# 🟡 CASUAL DETECTION
# ----------------------------------------
def detect_casual_intent(question: str):
    q = question.lower().strip()

    casual_patterns = [
        "hi", "hello", "hey",
        "good morning", "good evening",
        "how are you",
        "what's up",
        "who are you"
    ]

    for pattern in casual_patterns:
        # match whole words only
        if re.search(rf"\b{re.escape(pattern)}\b", q):
            return IntentModel(
                metric="none",
                time_range="none",
                comparison=None,
                filters={},
                query_type="casual",
                entity=None,
                product=None
            )

    return None


def safe_json_parse(text: str, question: str | None = None):
    try:
        parsed = json.loads(text)

        # ----------------------------------------
        # SAFE METRIC HANDLING
        # ----------------------------------------
        try:
            parsed["metric"] = canonicalize_metric(parsed["metric"])
        except:
            parsed["metric"] = parsed.get("metric", "net_sales").lower()

        intent = IntentModel(**parsed)

        if question:
            question_lower = question.lower()

            # ----------------------------------------
            # QUERY TYPE DETECTION
            # ----------------------------------------
            if any(w in question_lower for w in ["how many", "total", "count", "sum"]):
                intent.query_type = "direct"

            if any(w in question_lower for w in ["why", "underperform", "low", "drop"]):
                intent.query_type = "investigative"

            if any(w in question_lower for w in [
                "highest", "lowest", "top", "best", "worst",
                "max", "min", "most", "least"
            ]):
                intent.query_type = "analytical"

            # ----------------------------------------
            # METRIC OVERRIDE
            # ----------------------------------------
            if any(w in question_lower for w in ["unit", "units", "quantity", "qty"]):
                intent.metric = "units_sold"

            elif any(w in question_lower for w in ["sales", "revenue", "amount"]):
                intent.metric = "net_sales"

            # ----------------------------------------
            # ENTITY EXTRACTION
            # ----------------------------------------
            store_match = re.search(r"store\s*(\d+)", question_lower)
            if store_match:
                intent.entity = {
                    "type": "store",
                    "value": int(store_match.group(1))
                }

            region_match = re.search(r"region\s*([a-zA-Z]+)", question_lower)
            if region_match:
                intent.entity = {
                    "type": "region",
                    "value": region_match.group(1).capitalize()
                }

            # ----------------------------------------
            # PRODUCT EXTRACTION
            # ----------------------------------------
            product_match = re.search(r"product\s*([a-zA-Z0-9_ ]+)", question_lower)
            if product_match:
                intent.product = product_match.group(1).strip()

            # ----------------------------------------
            # FILTER MAPPING (SAFE)
            # ----------------------------------------
            if intent.entity:
                if intent.entity.get("type") == "store" and intent.entity.get("value") is not None:
                    intent.filters["StoreID"] = intent.entity["value"]

                if intent.entity.get("type") == "region" and intent.entity.get("value"):
                    intent.filters["Region"] = intent.entity["value"]

            if intent.product:
                intent.filters["ProductName"] = intent.product

            # ----------------------------------------
            # TOP N DETECTION
            # ----------------------------------------
            top_match = re.search(r"top\s*(\d+)", question_lower)
            if top_match:
                intent.filters["limit"] = int(top_match.group(1))

        return intent

    except (ValidationError, Exception) as e:
        raise Exception(f"Intent parsing failed: {str(e)}")


class IntentAgent(BaseAgent):
    name = "IntentAgent"

    def execute(self, state):

        # ----------------------------------------
        # 🟡 STEP 1: CASUAL SHORT-CIRCUIT
        # ----------------------------------------
        casual_intent = detect_casual_intent(state.question)
        if casual_intent:
            state.intent = casual_intent
            state.status = InvestigationStatus.IN_PROGRESS
            state.update_timestamp()

            print("[IntentAgent] Casual intent detected")

            return state

        # ----------------------------------------
        # 🟢 STEP 2: LLM INTENT
        # ----------------------------------------
        llm = get_llm()

        system_prompt = """
        You are a strict JSON generator.

        Extract structured analytics intent.

        Return ONLY valid JSON.

        Do NOT explain.
        Do NOT add text.
        Do NOT wrap in markdown.

        Format:
        {
        "metric": string,
        "time_range": string,
        "comparison": string | null,
        "filters": object
        }

        Examples:

        Q: Why did sales drop last week?
        A:
        {
        "metric": "net_sales",
        "time_range": "last_7_days",
        "comparison": "previous_period",
        "filters": {}
        }

        Q: Show revenue yesterday
        A:
        {
        "metric": "revenue",
        "time_range": "yesterday",
        "comparison": null,
        "filters": {}
        }
        """

        user_prompt = f"User question:\n{state.question}"

        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        try:
            intent = safe_json_parse(response.content, state.question)
        except (ValidationError, Exception) as e:
            raise Exception(f"Intent parsing failed: {str(e)}")

        state.intent = intent
        state.status = InvestigationStatus.IN_PROGRESS
        state.update_timestamp()

        print(f"[IntentAgent] Extracted intent: {state.intent}")

        return state