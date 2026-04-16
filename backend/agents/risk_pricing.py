"""
Agent 4: Risk Pricing Agent (Dynamic Premium AI)
Monitors live events, adjusts pricing mid-week. Like a real-time insurance advisor.
"""

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.base import (
    AgentState, invoke_with_structure, SYSTEM_PREAMBLE, format_context,
)


# ─── Pydantic Output Schema ─────────────────────────────────────────────────

class PricingDecision(BaseModel):
    """Structured output for dynamic risk pricing."""
    suggested_premium: float = Field(description="Suggested weekly premium in rupees")
    current_premium: float = Field(description="Current premium amount for comparison")
    risk_level: str = Field(description="Current risk level: LOW, MEDIUM, HIGH, CRITICAL")
    reasoning: str = Field(description="Detailed reasoning for the pricing recommendation")
    live_events: list[str] = Field(description="Active weather/risk events affecting pricing")
    coverage_suggestion: str = Field(description="Suggestion for coverage tier upgrade/downgrade")
    price_change_pct: float = Field(description="Percentage change from current premium")


# ─── LangGraph Nodes ─────────────────────────────────────────────────────────

def check_live_conditions(state: AgentState) -> dict:
    """Node 1: Check current live risk conditions for the worker's zone."""
    context = state["context"]
    zone_data = context.get("zone_data", {})

    # Build live event summary
    live_events = []
    flood_risk = zone_data.get("flood_risk_score", 50)
    heat_risk = zone_data.get("heat_risk_score", 50)
    aqi_risk = zone_data.get("aqi_risk_score", 50)
    strike_freq = zone_data.get("strike_frequency_yearly", 1.0)

    if flood_risk > 70:
        live_events.append(f"High flood risk ({flood_risk}%) — monsoon season active")
    if heat_risk > 50:
        live_events.append(f"Elevated heat risk ({heat_risk}%) — temperature warning")
    if aqi_risk > 60:
        live_events.append(f"Poor air quality risk ({aqi_risk}%) — AQI advisory")
    if strike_freq > 2.0:
        live_events.append(f"High strike frequency ({strike_freq}/year) — labor unrest zone")

    context["live_events"] = live_events
    context["overall_risk_score"] = (flood_risk * 0.35 + heat_risk * 0.20 + aqi_risk * 0.20 + min(strike_freq * 20, 100) * 0.25)
    return {"context": context}


def llm_price(state: AgentState) -> dict:
    """Node 2: LLM generates dynamic pricing recommendation."""
    context = state["context"]
    worker_data = context.get("worker_data", {})
    zone_data = context.get("zone_data", {})

    prompt = f"""You are a Risk Pricing Agent. Analyze current conditions and recommend 
optimal weekly insurance premium for this worker.

## Worker Profile
- Average Weekly Earnings: ₹{worker_data.get('avg_weekly_earnings', 4200)}
- Current Plan: {context.get('current_plan', 'STANDARD')}
- Current Premium: ₹{context.get('current_premium', 45)}
- Tenure: {worker_data.get('tenure_weeks', 0)} weeks
- Trust Score: {worker_data.get('trust_score', 50)}

## Zone Risk Profile
- Zone: {zone_data.get('zone_code', 'CHN-VEL-4B')}
- City: {zone_data.get('city', 'Chennai')}
- Flood Risk: {zone_data.get('flood_risk_score', 50)}%
- Heat Risk: {zone_data.get('heat_risk_score', 50)}%
- AQI Risk: {zone_data.get('aqi_risk_score', 50)}%
- Strike Frequency: {zone_data.get('strike_frequency_yearly', 1.0)}/year
- Overall Risk Score: {context.get('overall_risk_score', 50):.1f}

## Live Events
{chr(10).join(f'- {e}' for e in context.get('live_events', ['No active events']))}

Premium range: ₹29 (minimum) to ₹135 (maximum for PREMIUM tier).
Consider: zone risk, live events, worker tenure (loyal workers get discount), 
and whether the worker should upgrade their coverage tier."""

    result = invoke_with_structure(PricingDecision, SYSTEM_PREAMBLE, prompt)

    if result is None:
        current = context.get("current_premium", 45)
        risk = context.get("overall_risk_score", 50)
        suggested = round(29 + (risk / 100) * 46, 0)
        result = PricingDecision(
            suggested_premium=suggested,
            current_premium=current,
            risk_level="HIGH" if risk > 60 else ("MEDIUM" if risk > 30 else "LOW"),
            reasoning=f"Zone risk score is {risk:.1f}. Premium adjusted accordingly.",
            live_events=context.get("live_events", []),
            coverage_suggestion="Consider PREMIUM tier" if risk > 60 else "Current plan adequate",
            price_change_pct=round((suggested - current) / current * 100, 1) if current > 0 else 0,
        )

    return {"result": result.model_dump()}


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("check_live_conditions", check_live_conditions)
    builder.add_node("llm_price", llm_price)
    builder.set_entry_point("check_live_conditions")
    builder.add_edge("check_live_conditions", "llm_price")
    builder.add_edge("llm_price", END)
    return builder.compile()


class RiskPricingAgent:
    """Dynamic Risk Pricing Agent — real-time insurance advisor."""

    _graph = None

    @classmethod
    def get_graph(cls):
        if cls._graph is None:
            cls._graph = build_graph()
        return cls._graph

    @classmethod
    async def analyze(cls, worker_data: dict, zone_data: dict, current_plan: str = "STANDARD", current_premium: float = 45) -> dict:
        graph = cls.get_graph()
        initial_state = {
            "messages": [],
            "context": {
                "worker_data": worker_data,
                "zone_data": zone_data,
                "current_plan": current_plan,
                "current_premium": current_premium,
            },
            "result": {},
        }
        result = await graph.ainvoke(initial_state)
        return result["result"]
