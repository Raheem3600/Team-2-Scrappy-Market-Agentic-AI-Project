from app.agents.base import BaseAgent
from app.graph.state import IntentModel, InvestigationStatus
from app.config.llm import get_llm
from pydantic import ValidationError
from app.domain.metric_mapper import canonicalize_metric
import json
import re

def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise Exception("Invalid JSON output")


class IntentAgent(BaseAgent):
    name = "IntentAgent"

    def execute(self, state):
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

        user_prompt = f"""
User question:
{state.question}
"""

        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        try:
            parsed = safe_json_parse(response.content)
            parsed["metric"] = canonicalize_metric(parsed["metric"])
            intent = IntentModel(**parsed)
        except (ValidationError, Exception) as e:
            raise Exception(f"Intent parsing failed: {str(e)}")

        state.intent = intent
        state.status = InvestigationStatus.IN_PROGRESS
        state.update_timestamp()

        return state
