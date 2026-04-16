"""
Agent 2: Smart Trigger Validation Agent
Evaluates weather API reliability, historical patterns, sensor inconsistencies.
"""

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.base import (
    AgentState, invoke_with_structure, SYSTEM_PREAMBLE, format_context,
)


# ─── Pydantic Output Schema ─────────────────────────────────────────────────

class TriggerValidation(BaseModel):
    """Structured output for trigger validation."""
    is_valid: bool = Field(description="Whether the trigger event is genuine")
    confidence: float = Field(description="Confidence in the validation from 0.0 to 1.0")
    reasoning: str = Field(description="Detailed reasoning about source agreement and conflicts")
    source_reliability: dict = Field(description="Reliability assessment for each data source")
    recommendation: str = Field(description="One of: FIRE, HOLD, DISMISS")
    false_positive_risk: str = Field(description="Risk of this being a false positive: LOW, MEDIUM, HIGH")


# ─── LangGraph Nodes ─────────────────────────────────────────────────────────

def gather_sources(state: AgentState) -> dict:
    """Node 1: Gather data from all trigger sources."""
    context = state["context"]
    trigger_data = context.get("trigger_data", {})

    # Build source agreement matrix
    sources = {
        "primary_api": {
            "source": trigger_data.get("source_primary", "OpenWeatherMap"),
            "value": trigger_data.get("threshold_value"),
            "agrees": True,
        },
        "secondary_api": {
            "source": trigger_data.get("source_secondary", "IMD"),
            "value": trigger_data.get("threshold_value"),
            "agrees": trigger_data.get("sources_agreeing", 0) >= 2,
        },
        "tertiary_api": {
            "source": trigger_data.get("source_tertiary", "Platform Activity"),
            "agrees": trigger_data.get("sources_agreeing", 0) >= 3,
        },
    }

    context["source_matrix"] = sources
    context["sources_agreeing"] = trigger_data.get("sources_agreeing", 0)
    return {"context": context}


def llm_evaluate(state: AgentState) -> dict:
    """Node 2: LLM evaluates trigger validity with cross-source reasoning."""
    context = state["context"]
    trigger_data = context.get("trigger_data", {})
    source_matrix = context.get("source_matrix", {})

    prompt = f"""You are a Smart Trigger Validation Agent. Evaluate whether this parametric 
trigger event is genuine or a false positive.

## Trigger Event
- Type: {trigger_data.get('trigger_type', 'unknown')}
- Zone: {trigger_data.get('zone_code', 'unknown')}
- Severity: {trigger_data.get('severity', 'unknown')}
- Value Reported: {trigger_data.get('threshold_value')}
- Threshold Limit: {trigger_data.get('threshold_limit')}
- Auto-Approved: {trigger_data.get('auto_approved', False)}

## Source Agreement
- Sources Agreeing: {context.get('sources_agreeing', 0)}/3
{format_context(source_matrix)}

## Zone Context
- City: {context.get('city', 'Unknown')}
- Area: {context.get('area_name', 'Unknown')}
- Flood Risk Score: {context.get('flood_risk_score', 50)}
- Heat Risk Score: {context.get('heat_risk_score', 50)}
- AQI Risk Score: {context.get('aqi_risk_score', 50)}

Evaluate: Are the sources consistent? Is there contradictory evidence? 
Could this be a sensor malfunction or API error? Should we fire, hold, or dismiss?"""

    result = invoke_with_structure(TriggerValidation, SYSTEM_PREAMBLE, prompt)

    if result is None:
        sources_agreeing = context.get("sources_agreeing", 0)
        result = TriggerValidation(
            is_valid=sources_agreeing >= 2,
            confidence=sources_agreeing / 3.0,
            reasoning=f"{sources_agreeing}/3 sources agree on this trigger event.",
            source_reliability={"primary": "HIGH", "secondary": "MEDIUM", "tertiary": "LOW"},
            recommendation="FIRE" if sources_agreeing >= 3 else ("HOLD" if sources_agreeing >= 2 else "DISMISS"),
            false_positive_risk="LOW" if sources_agreeing >= 3 else ("MEDIUM" if sources_agreeing >= 2 else "HIGH"),
        )

    return {"result": result.model_dump()}


# ─── Graph Builder ───────────────────────────────────────────────────────────

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("gather_sources", gather_sources)
    builder.add_node("llm_evaluate", llm_evaluate)
    builder.set_entry_point("gather_sources")
    builder.add_edge("gather_sources", "llm_evaluate")
    builder.add_edge("llm_evaluate", END)
    return builder.compile()


# ─── Public API ──────────────────────────────────────────────────────────────

class TriggerValidatorAgent:
    """Smart Trigger Validation Agent — evaluates source reliability and conflicts."""

    _graph = None

    @classmethod
    def get_graph(cls):
        if cls._graph is None:
            cls._graph = build_graph()
        return cls._graph

    @classmethod
    async def validate(cls, trigger_data: dict, zone_data: dict = None) -> dict:
        """Validate a trigger event with AI cross-source analysis."""
        graph = cls.get_graph()
        zone_data = zone_data or {}

        initial_state = {
            "messages": [],
            "context": {
                "trigger_data": trigger_data,
                "city": zone_data.get("city", "Chennai"),
                "area_name": zone_data.get("area_name", "Velachery"),
                "flood_risk_score": zone_data.get("flood_risk_score", 50),
                "heat_risk_score": zone_data.get("heat_risk_score", 50),
                "aqi_risk_score": zone_data.get("aqi_risk_score", 50),
            },
            "result": {},
        }

        result = await graph.ainvoke(initial_state)
        return result["result"]
