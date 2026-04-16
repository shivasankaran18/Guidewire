"""
Agent 6: Worker Assistant Agent (UX Booster)
Simple chatbot that answers worker questions in plain language.
"Why did I get ₹1200?" / "Why was my claim delayed?"
"""

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.base import (
    AgentState, invoke_with_structure, SYSTEM_PREAMBLE, format_context,
)


# ─── Pydantic Output Schema ─────────────────────────────────────────────────

class WorkerResponse(BaseModel):
    """Structured output for worker assistant."""
    answer: str = Field(description="Clear, friendly answer in plain language (2-4 sentences)")
    category: str = Field(description="Question category: PAYOUT, CLAIM, POLICY, TRIGGER, ACCOUNT, GENERAL")
    related_claim_id: str = Field(default="", description="Related claim ID if applicable")
    suggested_actions: list[str] = Field(description="List of suggested next actions for the worker")
    sentiment: str = Field(description="Detected sentiment of the worker: HAPPY, NEUTRAL, CONFUSED, FRUSTRATED")


# ─── LangGraph Nodes ─────────────────────────────────────────────────────────

def understand_question(state: AgentState) -> dict:
    """Node 1: Parse the worker's question and gather relevant context."""
    context = state["context"]
    question = context.get("question", "")

    # Detect question category from keywords
    q_lower = question.lower()
    if any(w in q_lower for w in ["payout", "money", "paid", "₹", "rupees", "amount"]):
        category = "PAYOUT"
    elif any(w in q_lower for w in ["claim", "rejected", "denied", "delayed", "pending"]):
        category = "CLAIM"
    elif any(w in q_lower for w in ["policy", "plan", "coverage", "premium", "insurance"]):
        category = "POLICY"
    elif any(w in q_lower for w in ["rain", "flood", "heat", "aqi", "trigger", "weather"]):
        category = "TRIGGER"
    elif any(w in q_lower for w in ["account", "score", "trust", "status", "verified"]):
        category = "ACCOUNT"
    else:
        category = "GENERAL"

    context["detected_category"] = category
    return {"context": context}


def llm_explain(state: AgentState) -> dict:
    """Node 2: LLM generates a clear, friendly response."""
    context = state["context"]
    question = context.get("question", "")
    worker_data = context.get("worker_data", {})
    claim_data = context.get("claim_data", {})
    policy_data = context.get("policy_data", {})

    prompt = f"""You are a friendly Worker Assistant for GigPulse Sentinel. 
Answer the worker's question in simple, conversational Hindi-English (Hinglish) if appropriate, 
or clear English. Be empathetic and helpful.

## Worker's Question
"{question}"

## Worker Profile
- Name: {worker_data.get('name', 'Worker')}
- Platform: {worker_data.get('platform', 'Zomato')}
- Zone: {worker_data.get('primary_zone_code', 'Unknown')}
- Trust Score: {worker_data.get('trust_score', 50)}/100
- Account Status: {worker_data.get('account_status', 'ACTIVE')}
- Average Daily Earnings: ₹{worker_data.get('avg_daily_earnings', 700)}

## Recent Claim (if any)
- Claim Type: {claim_data.get('claim_type', 'N/A')}
- Status: {claim_data.get('status', 'N/A')}
- Calculated Payout: ₹{claim_data.get('calculated_payout', 0)}
- Actual Payout: ₹{claim_data.get('actual_payout', 0)}
- Fraud Score: {claim_data.get('fraud_score', 0)}
- Fraud Tier: {claim_data.get('fraud_tier', 'N/A')}

## Active Policy
- Plan: {policy_data.get('plan_tier', 'N/A')}
- Premium: ₹{policy_data.get('premium_amount', 0)}
- Coverage: ₹{policy_data.get('coverage_amount', 0)}

Answer the question clearly. If explaining a payout, break down the math.
If the claim was delayed, explain which fraud signals caused the hold.
Suggest 1-2 actions the worker can take."""

    result = invoke_with_structure(WorkerResponse, SYSTEM_PREAMBLE, prompt)

    if result is None:
        category = context.get("detected_category", "GENERAL")
        result = WorkerResponse(
            answer=f"Your question about {category.lower()} has been noted. Our team will review and respond shortly.",
            category=category,
            related_claim_id="",
            suggested_actions=["Check your claims history", "Contact support if urgent"],
            sentiment="NEUTRAL",
        )

    return {"result": result.model_dump()}


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("understand_question", understand_question)
    builder.add_node("llm_explain", llm_explain)
    builder.set_entry_point("understand_question")
    builder.add_edge("understand_question", "llm_explain")
    builder.add_edge("llm_explain", END)
    return builder.compile()


class WorkerAssistantAgent:
    """Worker Assistant — conversational AI that explains payouts, claims, and policies."""

    _graph = None

    @classmethod
    def get_graph(cls):
        if cls._graph is None:
            cls._graph = build_graph()
        return cls._graph

    @classmethod
    async def chat(
        cls,
        question: str,
        worker_data: dict = None,
        claim_data: dict = None,
        policy_data: dict = None,
    ) -> dict:
        graph = cls.get_graph()
        initial_state = {
            "messages": [],
            "context": {
                "question": question,
                "worker_data": worker_data or {},
                "claim_data": claim_data or {},
                "policy_data": policy_data or {},
            },
            "result": {},
        }
        result = await graph.ainvoke(initial_state)
        return result["result"]
