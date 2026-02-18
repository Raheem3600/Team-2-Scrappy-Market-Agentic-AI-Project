from app.agents.base import BaseAgent
from app.graph.state import IntentModel, InvestigationStatus
from app.config.llm import get_llm
from pydantic import ValidationError
import json


class IntentAgent(BaseAgent):
    name = "IntentAgent"

    def execute(self, state):
        llm = get_llm()

        system_prompt = """
You are a business analytics intent parser.

Extract structured intent from the user's question.

Return ONLY valid JSON with:
{
  "metric": string,
  "time_range": string,
  "comparison": string | null,
  "filters": object
}

Rules:
- metric must be canonical (e.g., net_sales, revenue, orders)
- time_range must be normalized (e.g., last_7_days, yesterday)
- comparison can be previous_period or null
- filters default to empty object
"""

        user_prompt = f"""
User question:
{state.question}
"""

        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        try:
            parsed = json.loads(response.content)
            print(parsed)
            intent = IntentModel(**parsed)
            print(intent)
        except (json.JSONDecodeError, ValidationError) as e:
            raise Exception(f"Intent parsing failed: {str(e)}")

        state.intent = intent
        state.status = InvestigationStatus.IN_PROGRESS
        state.update_timestamp()

        return state
