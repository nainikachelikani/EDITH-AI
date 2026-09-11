"""
FastMCP Tools Implementation for SENTINEL.
Provides real, functional MCP tools for accessibility retrieval, action context analysis,
safety policy lookup, and event logging.
"""
import json
import time
import uuid
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from config.settings import settings
from rag.retriever import retriever
from models.schemas import RetrievedDocument

mcp_app = FastMCP(name="SentinelMCP")

@mcp_app.tool()
def retrieve_accessibility_guidance(query: str, top_k: int = 4) -> Dict[str, Any]:
    """
    Queries ChromaDB accessibility knowledge base for WCAG guidelines and inclusive patterns.
    Returns matched documents, relevance scores, and recommended alternatives.
    """
    start_time = time.time()
    try:
        docs = retriever.retrieve(query_text=query, top_k=top_k)
        exec_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "success": True,
            "query": query,
            "count": len(docs),
            "documents": [d.model_dump() for d in docs],
            "execution_time_ms": exec_ms
        }
    except Exception as e:
        exec_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "documents": [],
            "execution_time_ms": exec_ms
        }

@mcp_app.tool()
def analyze_action_context(action_type: str, target: str, description: str) -> Dict[str, Any]:
    """
    Analyzes proposed computer action metadata to extract modality, reversibility hints,
    and potential accessibility problem patterns.
    """
    start_time = time.time()
    action_lower = f"{action_type} {target} {description}".lower()
    
    # Analyze interaction modality
    modality = "unknown"
    if any(m in action_lower for m in ["drag", "drop", "hover", "right-click", "contextmenu"]):
        modality = "mouse_dependent"
    elif any(m in action_lower for m in ["type", "press", "key", "tab", "enter", "space"]):
        modality = "keyboard_compatible"
    elif any(m in action_lower for m in ["click", "select", "tap", "navigate"]):
        modality = "pointer_or_keyboard"

    # Potential barrier hints
    potential_barrier = False
    barrier_hint = "None"
    if "drag" in action_lower:
        potential_barrier = True
        barrier_hint = "Dragging interaction without single-pointer alternative (WCAG 2.5.7)"
    elif "hover" in action_lower:
        potential_barrier = True
        barrier_hint = "Hover-triggered action without keyboard equivalent (WCAG 1.4.13)"
    elif "icon" in action_lower and not any(k in action_lower for k in ["label", "text", "name", "aria"]):
        potential_barrier = True
        barrier_hint = "Possible icon-only button without accessible label (WCAG 4.1.2)"

    exec_ms = round((time.time() - start_time) * 1000, 2)
    return {
        "success": True,
        "action_type": action_type,
        "target": target,
        "modality": modality,
        "potential_barrier": potential_barrier,
        "barrier_hint": barrier_hint,
        "execution_time_ms": exec_ms
    }

@mcp_app.tool()
def get_safety_policy(action_type: str, target: str, impact_description: str) -> Dict[str, Any]:
    """
    Evaluates proposed action against configurable safety policies in data/safety_policy.json.
    Returns matched policy rules and recommended mitigation instructions.
    """
    start_time = time.time()
    policy_path = settings.storage.safety_policy_path
    
    try:
        with open(policy_path, "r", encoding="utf-8") as f:
            policies_data = json.load(f).get("policies", [])
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load safety policy file: {e}",
            "applicable_policies": [],
            "requires_confirmation": False,
            "execution_time_ms": round((time.time() - start_time) * 1000, 2)
        }

    combined_text = f"{action_type} {target} {impact_description}".lower()
    applicable = []
    requires_confirmation = False
    highest_impact = "LOW"
    recommendation = "APPROVE"

    impact_ranks = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

    for p in policies_data:
        conditions = p.get("applicable_conditions", {})
        categories = conditions.get("operation_categories", [])
        
        # Check if category keywords match
        if any(cat in combined_text for cat in categories):
            applicable.append({
                "id": p["id"],
                "name": p["name"],
                "impact_level": p["impact_level"],
                "recommendation": p["policy_recommendation"],
                "mitigation_instructions": p["mitigation_instructions"]
            })
            if p.get("requires_confirmation"):
                requires_confirmation = True
            
            p_impact = p.get("impact_level", "LOW")
            if impact_ranks.get(p_impact, 1) > impact_ranks.get(highest_impact, 1):
                highest_impact = p_impact
                recommendation = p.get("policy_recommendation", "BLOCK")

    exec_ms = round((time.time() - start_time) * 1000, 2)
    return {
        "success": True,
        "applicable_policies": applicable,
        "policy_count": len(applicable),
        "requires_confirmation": requires_confirmation,
        "highest_impact": highest_impact,
        "policy_recommendation": recommendation,
        "execution_time_ms": exec_ms
    }

@mcp_app.tool()
def log_sentinel_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Writes a structured execution event to persistent JSONL trace storage.
    Returns the event ID and timestamp.
    """
    start_time = time.time()
    trace_path = settings.storage.trace_path
    event_id = event_data.get("trace_id") or f"trace_{uuid.uuid4().hex[:12]}"
    
    record = {
        "trace_id": event_id,
        "timestamp": event_data.get("timestamp") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workflow_id": event_data.get("workflow_id", "default"),
        "agent_name": event_data.get("agent_name", "sentinel_core"),
        "payload": event_data
    }

    try:
        with open(trace_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        exec_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "success": True,
            "event_id": event_id,
            "trace_path": trace_path,
            "execution_time_ms": exec_ms
        }
    except Exception as e:
        exec_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "success": False,
            "error": str(e),
            "event_id": event_id,
            "execution_time_ms": exec_ms
        }
