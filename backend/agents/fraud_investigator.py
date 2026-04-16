"""
Agent 1: Fraud Investigation Agent (HIGH IMPACT)
Reads all signals, explains suspicion, decides: approve / reject / escalate.
"""

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.base import (
    AgentState, invoke_with_structure, SYSTEM_PREAMBLE, format_context,
)
from backend.services.fraud_detector import FraudDetector


# ─── Pydantic Output Schema ─────────────────────────────────────────────────

class FraudInvestigation(BaseModel):
    """Structured output for fraud investigation."""
    decision: str = Field(description="One of: APPROVE, REJECT, ESCALATE")
    reasoning: str = Field(description="Detailed reasoning explaining the decision step by step")
    suspicious_signals: list[str] = Field(description="List of suspicious signal names detected")
    confidence: float = Field(description="Confidence in the decision from 0.0 to 1.0")
    explanation_for_worker: str = Field(description="Simple, friendly explanation for the worker in plain language")
    risk_level: str = Field(description="Overall risk level: LOW, MEDIUM, HIGH, CRITICAL")


# ─── LangGraph Nodes ─────────────────────────────────────────────────────────

def gather_signals(state: AgentState) -> dict:
    """Node 1: Gather all fraud signals from existing detector."""
    context = state["context"]
    worker_data = context.get("worker_data", {})
    location_data = context.get("location_data", {})
    device_data = context.get("device_data", {})
    platform_data = context.get("platform_data", {})

    # Run existing 7-signal fraud analysis
    analysis = FraudDetector.analyze_claim(
        worker_data=worker_data,
        location_data=location_data,
        device_data=device_data,
        platform_data=platform_data,
    )

    context["fraud_analysis"] = analysis
    return {"context": context}


def llm_reason(state: AgentState) -> dict:
    """Node 2: LLM reasons over all signals and makes a decision."""
    context = state["context"]
    analysis = context.get("fraud_analysis", {})

    prompt = f"""You are a Fraud Investigation Agent. Analyze the following claim signals 
and make a clear decision: APPROVE, REJECT, or ESCALATE.

## Claim Context
- Worker ID: {context.get('worker_id', 'unknown')}
- Claim Type: {context.get('claim_type', 'unknown')}
- Zone Code: {context.get('zone_code', 'unknown')}
- Disruption Hours: {context.get('disruption_hours', 0)}

## Fraud Analysis (7-Signal Scoring)
- Overall Fraud Score: {analysis.get('fraud_score', 0)}/100
- Current Tier: {analysis.get('fraud_tier', 'unknown')}
- Confidence Score: {analysis.get('confidence_score', 0)}%

## Individual Signal Breakdown
{format_context(analysis.get('signals', {}))}

## Flagged Signals
{analysis.get('flagged_signals', [])}

Based on ALL signals, provide your investigation decision with detailed reasoning.
Be specific about which signals are concerning and why.
If the worker is genuine, explain why the signals support that conclusion."""

    result = invoke_with_structure(FraudInvestigation, SYSTEM_PREAMBLE, prompt)

    if result is None:
        # Fallback: use the existing rule-based analysis
        tier = analysis.get("fraud_tier", "GREEN")
        result = FraudInvestigation(
            decision="APPROVE" if tier == "GREEN" else ("ESCALATE" if tier == "AMBER" else "REJECT"),
            reasoning=analysis.get("recommendation", "Rule-based decision"),
            suspicious_signals=analysis.get("flagged_signals", []),
            confidence=analysis.get("confidence_score", 50) / 100,
            explanation_for_worker="Your claim is being processed." if tier == "GREEN" else "Your claim requires additional verification.",
            risk_level="LOW" if tier == "GREEN" else ("MEDIUM" if tier == "AMBER" else "HIGH"),
        )

    return {"result": result.model_dump()}


# ─── Graph Builder ───────────────────────────────────────────────────────────

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("gather_signals", gather_signals)
    builder.add_node("llm_reason", llm_reason)
    builder.set_entry_point("gather_signals")
    builder.add_edge("gather_signals", "llm_reason")
    builder.add_edge("llm_reason", END)
    return builder.compile()


# ─── Public API ──────────────────────────────────────────────────────────────

class FraudInvestigatorAgent:
    """Fraud Investigation Agent — explains why something is suspicious and decides."""

    _graph = None

    @classmethod
    def get_graph(cls):
        if cls._graph is None:
            cls._graph = build_graph()
        return cls._graph

    @classmethod
    async def investigate(
        cls,
        worker_id: str,
        claim_type: str = "HEAVY_RAIN",
        zone_code: str = "CHN-VEL-4B",
        disruption_hours: float = 4.0,
        location_data: dict = None,
        device_data: dict = None,
        platform_data: dict = None,
    ) -> dict:
        """Run a full fraud investigation on a claim."""
        graph = cls.get_graph()

        initial_state = {
            "messages": [],
            "context": {
                "worker_id": worker_id,
                "claim_type": claim_type,
                "zone_code": zone_code,
                "disruption_hours": disruption_hours,
                "worker_data": {"tenure_weeks": 24},
                "location_data": location_data or {
                    "velocity_kmh": 25, "max_velocity_kmh": 45,
                    "zone_match_30d": True, "days_in_zone_30d": 22,
                    "altitude_variance": 8.5, "gps_cell_distance_km": 0.8,
                },
                "device_data": device_data or {
                    "is_rooted": False, "mock_gps_detected": False,
                    "is_emulator": False, "motion_level": 0.72,
                },
                "platform_data": platform_data or {
                    "has_orders_in_zone": True, "order_count_today": 8,
                },
            },
            "result": {},
        }

        result = await graph.ainvoke(initial_state)
        return result["result"]
