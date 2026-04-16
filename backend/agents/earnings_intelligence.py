"""
Agent 3: Earnings Intelligence Agent
Learns worker behavior patterns, festival spikes, area demand shifts.
Moves from static ML to adaptive intelligence.
"""

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.base import (
    AgentState, invoke_with_structure, SYSTEM_PREAMBLE, format_context,
)


# ─── Pydantic Output Schema ─────────────────────────────────────────────────

class EarningsInsight(BaseModel):
    """Structured output for earnings intelligence."""
    adjusted_payout: float = Field(description="AI-adjusted payout amount in rupees")
    original_payout: float = Field(description="Original calculated payout before adjustment")
    adjustment_reason: str = Field(description="Why the payout was adjusted up or down")
    pattern_detected: str = Field(description="The key earnings pattern detected for this worker")
    peak_hours: list[str] = Field(description="Worker's peak earning hours as strings like '18:00-21:00'")
    demand_multiplier: float = Field(description="Demand multiplier applied based on time/day patterns")
    recommendation: str = Field(description="Suggested action or insight for the system")


# ─── LangGraph Nodes ─────────────────────────────────────────────────────────

def load_earnings_dna(state: AgentState) -> dict:
    """Node 1: Load worker's earnings DNA profile."""
    context = state["context"]
    worker_data = context.get("worker_data", {})

    # Build earnings profile from available data
    earnings_profile = {
        "avg_daily": worker_data.get("avg_daily_earnings", 700),
        "avg_weekly": worker_data.get("avg_weekly_earnings", 4200),
        "tenure_weeks": worker_data.get("tenure_weeks", 24),
        "zone": worker_data.get("primary_zone_code", "CHN-VEL-4B"),
        "platform": worker_data.get("platform", "zomato"),
    }

    # Simulate earnings DNA patterns (from EarningsDNA model)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    disruption_day = context.get("disruption_day", 5)  # Saturday default
    disruption_hour = context.get("disruption_hour", 19)  # 7 PM default

    # Peak hour detection
    peak_hours = []
    if disruption_hour >= 11 and disruption_hour <= 14:
        peak_hours = ["11:00-14:00 (lunch rush)"]
        demand_mult = 1.8
    elif disruption_hour >= 18 and disruption_hour <= 21:
        peak_hours = ["18:00-21:00 (dinner rush)"]
        demand_mult = 2.2
    elif disruption_hour >= 6 and disruption_hour <= 9:
        peak_hours = ["06:00-09:00 (breakfast)"]
        demand_mult = 1.3
    else:
        peak_hours = ["off-peak hours"]
        demand_mult = 0.8

    # Weekend bonus
    if disruption_day >= 5:
        demand_mult *= 1.3
        peak_hours.append("Weekend bonus active")

    context["earnings_profile"] = earnings_profile
    context["peak_hours"] = peak_hours
    context["demand_multiplier"] = round(demand_mult, 2)
    context["disruption_day_name"] = day_names[disruption_day]
    return {"context": context}


def llm_interpret(state: AgentState) -> dict:
    """Node 2: LLM interprets earnings patterns and adjusts payout dynamically."""
    context = state["context"]
    earnings = context.get("earnings_profile", {})

    original_payout = context.get("original_payout", 700)
    demand_mult = context.get("demand_multiplier", 1.0)

    prompt = f"""You are an Earnings Intelligence Agent. Analyze this worker's earnings 
patterns and recommend a dynamically adjusted payout.

## Worker Profile
- Average Daily Earnings: ₹{earnings.get('avg_daily', 700)}
- Average Weekly Earnings: ₹{earnings.get('avg_weekly', 4200)}
- Platform: {earnings.get('platform', 'zomato')}
- Tenure: {earnings.get('tenure_weeks', 0)} weeks
- Zone: {earnings.get('zone', 'CHN-VEL-4B')}

## Disruption Context
- Day: {context.get('disruption_day_name', 'Saturday')}
- Hour: {context.get('disruption_hour', 19)}:00
- Disruption Hours: {context.get('disruption_hours', 4)}
- Original Calculated Payout: ₹{original_payout}

## Detected Patterns
- Peak Hours: {context.get('peak_hours', [])}
- Demand Multiplier: {demand_mult}x

Should the payout be adjusted based on this worker's earning patterns?
Consider: peak vs off-peak, weekend vs weekday, worker's actual earnings history.
The adjusted payout should be fair — not inflated, but reflective of real lost income."""

    result = invoke_with_structure(EarningsInsight, SYSTEM_PREAMBLE, prompt)

    if result is None:
        adjusted = round(original_payout * demand_mult, 2)
        result = EarningsInsight(
            adjusted_payout=adjusted,
            original_payout=original_payout,
            adjustment_reason=f"Demand multiplier {demand_mult}x applied for peak hours",
            pattern_detected=f"Peak earnings during {context.get('peak_hours', ['unknown'])[0]}",
            peak_hours=context.get("peak_hours", []),
            demand_multiplier=demand_mult,
            recommendation=f"Payout adjusted from ₹{original_payout} to ₹{adjusted} based on earnings DNA",
        )

    return {"result": result.model_dump()}


# ─── Graph Builder ───────────────────────────────────────────────────────────

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("load_earnings_dna", load_earnings_dna)
    builder.add_node("llm_interpret", llm_interpret)
    builder.set_entry_point("load_earnings_dna")
    builder.add_edge("load_earnings_dna", "llm_interpret")
    builder.add_edge("llm_interpret", END)
    return builder.compile()


class EarningsIntelligenceAgent:
    """Earnings Intelligence — adaptive payout based on worker behavior patterns."""

    _graph = None

    @classmethod
    def get_graph(cls):
        if cls._graph is None:
            cls._graph = build_graph()
        return cls._graph

    @classmethod
    async def analyze(
        cls,
        worker_data: dict,
        original_payout: float = 700,
        disruption_hours: float = 4.0,
        disruption_day: int = 5,
        disruption_hour: int = 19,
    ) -> dict:
        graph = cls.get_graph()

        initial_state = {
            "messages": [],
            "context": {
                "worker_data": worker_data,
                "original_payout": original_payout,
                "disruption_hours": disruption_hours,
                "disruption_day": disruption_day,
                "disruption_hour": disruption_hour,
            },
            "result": {},
        }

        result = await graph.ainvoke(initial_state)
        return result["result"]
