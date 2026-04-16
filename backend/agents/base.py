"""
GigPulse Sentinel — Agent Base Infrastructure
Shared Cerebras LLM client, LangGraph state, and helpers.
"""

import os
import json
import re
from typing import TypedDict, Annotated, Any
from pydantic import BaseModel, Field
from langchain_cerebras import ChatCerebras
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# ─── Cerebras LLM Client ────────────────────────────────────────────────────

_llm_instance = None

def get_llm() -> ChatCerebras:
    """Get a singleton ChatCerebras instance."""
    global _llm_instance
    if _llm_instance is None:
        api_key = os.getenv("CEREBRAS_API_KEY", "")
        # Handle empty API key gracefully - use placeholder for testing
        if not api_key:
            api_key = "mock-key-for-testing"
        # Cast to str to satisfy type checker - actual SecretStr handled by library
        _llm_instance = ChatCerebras(
            model="llama3.1-8b",
            api_key=api_key,  # type: ignore
            temperature=0.3,
            max_tokens=2048,
        )
    return _llm_instance


def get_structured_llm(pydantic_model):
    """Get an LLM bound to a Pydantic model for structured output."""
    return get_llm().with_structured_output(pydantic_model)


def invoke_with_structure(pydantic_model, system_prompt: str, user_prompt: str):
    """
    Invoke Cerebras LLM and parse the response into a Pydantic model.
    Uses JSON instruction in the prompt + manual parsing for reliability
    with smaller models like llama3.1-8b.
    """
    # Build the JSON schema hint for the model
    schema = pydantic_model.model_json_schema()
    fields_hint = {}
    for field_name, field_info in schema.get("properties", {}).items():
        fields_hint[field_name] = field_info.get("description", field_info.get("type", "string"))

    json_instruction = (
        f"\n\nYou MUST respond with ONLY a valid JSON object matching this schema:\n"
        f"```json\n{json.dumps(fields_hint, indent=2)}\n```\n"
        f"Do NOT include any text outside the JSON. Start with {{ and end with }}."
    )

    llm = get_llm()
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt + json_instruction),
            HumanMessage(content=user_prompt),
        ])

        # Handle different response formats
        content = response.content
        if isinstance(content, list):
            # If it's a list, join the string parts
            content = " ".join(str(item) for item in content)
        elif not isinstance(content, str):
            content = str(content)
        
        content = content.strip()

        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1).strip()

        # Try to find JSON object in the response
        brace_start = content.find('{')
        brace_end = content.rfind('}')
        if brace_start != -1 and brace_end != -1:
            content = content[brace_start:brace_end + 1]

        data = json.loads(content)

        # Fix common issues: string values that should be numbers (e.g., "₹796" -> 796)
        for field_name, field_info in schema.get("properties", {}).items():
            if field_info.get("type") in ("number", "float") and field_name in data:
                if isinstance(data[field_name], str):
                    # Remove currency symbols, commas, and trailing characters
                    cleaned = re.sub(r'[₹,\s\[\]a-zA-Z]', '', data[field_name])
                    try:
                        data[field_name] = float(cleaned) if '.' in cleaned else int(cleaned)
                    except ValueError:
                        data[field_name] = 0.0

            # Fix common issues: string values that should be booleans
            if field_info.get("type") == "boolean" and field_name in data:
                if isinstance(data[field_name], str):
                    lower_val = data[field_name].lower().strip()
                    if lower_val in ("true", "yes", "confirmed", "1"):
                        data[field_name] = True
                    elif lower_val in ("false", "no", "dismissed", "0"):
                        data[field_name] = False

            # Fix common issues: string lists that should be actual lists
            if field_info.get("type") == "array" and field_name in data:
                if isinstance(data[field_name], str):
                    try:
                        data[field_name] = json.loads(data[field_name])
                    except json.JSONDecodeError:
                        data[field_name] = [data[field_name]]
            
            # Fix dict fields that come as strings
            if field_info.get("type") == "object" and field_name in data:
                if isinstance(data[field_name], str):
                    try:
                        data[field_name] = json.loads(data[field_name])
                    except json.JSONDecodeError:
                        data[field_name] = {}

        return pydantic_model.model_validate(data)

    except Exception as e:
        print(f"⚠️ LLM structured invocation failed: {e}")
        return None


# ─── LangGraph Shared State ─────────────────────────────────────────────────

class AgentState(TypedDict):
    """Common state shared across all agent graphs."""
    messages: Annotated[list, add_messages]
    context: dict         # DB-fetched data (claims, signals, worker info, etc.)
    result: dict          # Final structured output from the agent


# ─── Prompt Helpers ──────────────────────────────────────────────────────────

SYSTEM_PREAMBLE = (
    "You are an AI agent for GigPulse Sentinel, an AI-powered parametric income "
    "protection system for gig delivery workers in India. You make decisions based "
    "on data signals including GPS, device fingerprints, weather data, platform "
    "order logs, and earnings patterns. Always provide clear, explainable reasoning "
    "for your decisions. Be precise with numbers and specific about which signals "
    "informed your judgment."
)


def format_context(data: dict) -> str:
    """Format a context dict into a clean string for the LLM prompt."""
    parts = []
    for key, value in data.items():
        if isinstance(value, dict):
            formatted = json.dumps(value, indent=2, default=str)
            parts.append(f"### {key.replace('_', ' ').title()}\n```json\n{formatted}\n```")
        elif isinstance(value, list):
            formatted = json.dumps(value, indent=2, default=str)
            parts.append(f"### {key.replace('_', ' ').title()}\n```json\n{formatted}\n```")
        else:
            parts.append(f"**{key.replace('_', ' ').title()}:** {value}")
    return "\n\n".join(parts)


def safe_invoke(llm, messages: list) -> Any:
    """Invoke LLM with error handling. Returns None on failure."""
    try:
        return llm.invoke(messages)
    except Exception as e:
        print(f"⚠️ LLM invocation failed: {e}")
        return None
