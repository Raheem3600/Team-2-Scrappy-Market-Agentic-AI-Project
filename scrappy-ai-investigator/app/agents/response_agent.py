from app.agents.base import BaseAgent
from app.graph.state import InvestigationState
from app.config.llm import get_llm


class ResponseAgent(BaseAgent):
    name = "ResponseAgent"

    def __init__(self):
        self.llm = get_llm()

    def execute(self, state: InvestigationState):

        if not state.hypotheses:
            state.final_answer = "No hypotheses generated."
            state.status = "completed"
            return state

        # Best hypothesis
        best = max(
            state.hypotheses,
            key=lambda h: h.score if h.score is not None else 0
        )

        confidence = state.confidence or 0

        # Collect evidence summary
        evidence_text = ""
        for e in state.evidence:
            evidence_text += f"\nHypothesis: {e.hypothesis}\n"
            evidence_text += f"Summary: {e.summary}\n"
            evidence_text += f"Sample Data: {str(e.raw_data[:2])}\n"

        # 🧠 Prompt
        prompt = f"""
You are a senior retail data analyst.

User Question:
{state.question}

Top Hypothesis:
{best.name} (score: {best.score})

Confidence:
{confidence}

Evidence:
{evidence_text}

Instructions:
- Explain what is happening in simple business terms
- Identify possible causes
- Keep it concise (3-5 sentences)
- Do NOT mention technical terms like SQL, tables, or raw JSON

Answer:
"""

        # 🔥 LLM call
        response = self.llm.invoke(prompt)

        state.final_answer = response.content
        state.status = "completed"

        return state
