"""
LangGraph Workflow for SENTINEL.
Orchestrates multi-agent supervisory pipeline with ChromaDB RAG, FastMCP tools,
per-action isolation, dynamic REPLACE loop, human confirmation, and JSONL tracing.
"""
import time
import uuid
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END

from config.settings import settings
from models.schemas import (
    ActionItem,
    ActionPlan,
    RetrievedDocument,
    AccessibilityResult,
    RiskResult,
    ConfidenceResult,
    DecisionResult,
    NarrationResult
)
from models.state import SentinelState
from agents.intent_agent import intent_agent
from agents.action_planner import action_planner
from agents.accessibility_agent import accessibility_agent
from agents.risk_agent import risk_agent
from agents.confidence_agent import confidence_agent
from agents.decision_agent import decision_agent
from agents.narrator_agent import narrator_agent
from sentinel_mcp.client import mcp_client
from services.trace_service import trace_service

# ----------------- NODE DEFINITIONS -----------------

def intent_node(state: SentinelState) -> Dict[str, Any]:
    start = time.time()
    user_req = state.get("user_request", "")
    intent_res = intent_agent.run(user_req)
    exec_ms = (time.time() - start) * 1000
    
    trace_service.log_event(
        workflow_id=state.get("workflow_id", "default"),
        agent_name="IntentAgent",
        input_summary={"user_request": user_req},
        output_summary=intent_res.model_dump(),
        execution_time_ms=exec_ms
    )
    return {
        "intent": intent_res,
        "domain": intent_res.domain
    }

def planner_node(state: SentinelState) -> Dict[str, Any]:
    start = time.time()
    intent = state.get("intent")
    plan = action_planner.run(intent)
    exec_ms = (time.time() - start) * 1000

    trace_service.log_event(
        workflow_id=state.get("workflow_id", "default"),
        agent_name="ActionPlannerAgent",
        input_summary={"goal": intent.goal},
        output_summary=plan.model_dump(),
        execution_time_ms=exec_ms
    )
    return {
        "action_plan": plan,
        "current_action_index": 0,
        "action_evaluations": []
    }

def prepare_action_node(state: SentinelState) -> Dict[str, Any]:
    plan = state.get("action_plan")
    idx = state.get("current_action_index", 0)
    
    if plan and plan.actions and idx < len(plan.actions):
        current_action = plan.actions[idx]
    else:
        current_action = None

    # Reset per-action dynamic analysis state
    return {
        "current_action": current_action,
        "replacement_attempt_count": 0,
        "retrieved_documents": [],
        "accessibility_result": None,
        "risk_result": None,
        "confidence_result": None,
        "decision_result": None,
        "narration": None,
        "requires_confirmation": False,
        "mcp_tool_calls": []
    }

def retrieval_node(state: SentinelState) -> Dict[str, Any]:
    action = state.get("current_action")
    if not action:
        return {"retrieved_documents": []}
    
    query = f"{action.action_type} {action.target} {action.description}"
    # Invoke real FastMCP tool via SentinelMCPClient
    mcp_call = mcp_client.call_tool("retrieve_accessibility_guidance", {"query": query, "top_k": settings.rag.top_k})
    tool_calls = list(state.get("mcp_tool_calls", []))
    tool_calls.append(mcp_call)
    
    docs_raw = mcp_call.get("result", {}).get("documents", [])
    docs = [RetrievedDocument(**d) for d in docs_raw]
    return {
        "retrieved_documents": docs,
        "mcp_tool_calls": tool_calls
    }

def accessibility_node(state: SentinelState) -> Dict[str, Any]:
    action = state.get("current_action")
    docs = state.get("retrieved_documents", [])
    acc_res = accessibility_agent.run(action=action, retrieved_docs=docs)
    return {"accessibility_result": acc_res}

def risk_node(state: SentinelState) -> Dict[str, Any]:
    action = state.get("current_action")
    # Invoke real FastMCP tool via SentinelMCPClient
    mcp_call = mcp_client.call_tool("get_safety_policy", {
        "action_type": action.action_type,
        "target": action.target,
        "impact_description": action.description
    })
    tool_calls = list(state.get("mcp_tool_calls", []))
    tool_calls.append(mcp_call)

    policy_context = mcp_call.get("result", {})
    risk_res = risk_agent.run(action=action, policy_context=policy_context)
    return {
        "risk_result": risk_res,
        "_policy_context": policy_context,
        "mcp_tool_calls": tool_calls
    }

def confidence_node(state: SentinelState) -> Dict[str, Any]:
    docs = state.get("retrieved_documents", [])
    acc_res = state.get("accessibility_result")
    risk_res = state.get("risk_result")
    conf_res = confidence_agent.calculate(
        retrieved_docs=docs,
        accessibility_res=acc_res,
        risk_res=risk_res
    )
    return {"confidence_result": conf_res}

def decision_node(state: SentinelState) -> Dict[str, Any]:
    action = state.get("current_action")
    acc_res = state.get("accessibility_result")
    risk_res = state.get("risk_result")
    conf_res = state.get("confidence_result")
    pol_ctx = state.get("_policy_context", {})
    
    dec_res = decision_agent.run(
        action=action,
        accessibility_res=acc_res,
        risk_res=risk_res,
        confidence_res=conf_res,
        policy_context=pol_ctx
    )
    return {
        "decision_result": dec_res,
        "requires_confirmation": dec_res.requires_human_confirmation,
        "human_confirmation_status": dec_res.human_confirmation_status
    }

def replacement_node(state: SentinelState) -> Dict[str, Any]:
    """
    Handles dynamic replacement loop (Modification 5).
    Converts accessible alternative into a new action and increments attempt counter.
    """
    action = state.get("current_action")
    acc_res = state.get("accessibility_result")
    attempts = state.get("replacement_attempt_count", 0) + 1
    
    alt_text = acc_res.alternative or "Use standard keyboard accessible button or controls."
    new_action = ActionItem(
        id=f"{action.id}_alt",
        action_type="keyboard_accessible_command",
        target=action.target,
        description=f"Accessible Alternative: {alt_text}",
        reversible=action.reversible,
        data_sensitivity=action.data_sensitivity
    )
    return {
        "current_action": new_action,
        "replacement_attempt_count": attempts
    }

def human_confirmation_node(state: SentinelState) -> Dict[str, Any]:
    """
    Human-In-The-Loop node (Modification 6).
    Updates status based on whether confirmation is granted, cancelled, or overridden.
    """
    status = state.get("human_confirmation_status", "PENDING_CONFIRMATION")
    return {"human_confirmation_status": status}

def narrator_node(state: SentinelState) -> Dict[str, Any]:
    action = state.get("current_action")
    acc_res = state.get("accessibility_result")
    risk_res = state.get("risk_result")
    conf_res = state.get("confidence_result")
    dec_res = state.get("decision_result")
    
    narration = narrator_agent.run(
        action=action,
        accessibility_res=acc_res,
        risk_res=risk_res,
        confidence_res=conf_res,
        decision_res=dec_res
    )
    return {"narration": narration}

def trace_logger_node(state: SentinelState) -> Dict[str, Any]:
    action = state.get("current_action")
    acc = state.get("accessibility_result")
    risk = state.get("risk_result")
    conf = state.get("confidence_result")
    dec = state.get("decision_result")
    narr = state.get("narration")
    evals = state.get("action_evaluations", [])

    # Real FastMCP tool invocation via SentinelMCPClient
    mcp_call = mcp_client.call_tool("log_sentinel_event", {
        "event_data": {
            "workflow_id": state.get("workflow_id", "default"),
            "agent_name": "DecisionPipeline",
            "action_id": action.id if action else "none",
            "decision": dec.decision if dec else "UNKNOWN",
            "confidence": conf.overall_confidence if conf else 0.0,
            "human_status": state.get("human_confirmation_status")
        }
    })
    tool_calls = list(state.get("mcp_tool_calls", []))
    tool_calls.append(mcp_call)

    action_summary = {
        "action": action.model_dump() if action else {},
        "accessibility": acc.model_dump() if acc else {},
        "risk": risk.model_dump() if risk else {},
        "confidence": conf.model_dump() if conf else {},
        "decision": dec.model_dump() if dec else {},
        "narration": narr.model_dump() if narr else {},
        "human_status": state.get("human_confirmation_status"),
        "mcp_tool_calls": tool_calls
    }
    evals.append(action_summary)

    next_idx = state.get("current_action_index", 0) + 1
    return {
        "action_evaluations": evals,
        "mcp_tool_calls": tool_calls,
        "current_action_index": next_idx
    }

# ----------------- CONDITIONAL ROUTING -----------------

def route_after_decision(state: SentinelState) -> Literal["replacement_node", "human_confirmation_node", "narrator_node"]:
    dec = state.get("decision_result")
    attempts = state.get("replacement_attempt_count", 0)
    max_attempts = settings.policies.max_replacement_attempts

    if dec and dec.decision == "REPLACE":
        if attempts < max_attempts:
            return "replacement_node"
        else:
            # Fallback to escalation if replacement attempts exceeded
            return "human_confirmation_node"
    
    if dec and dec.decision in ["BLOCK", "ESCALATE"]:
        return "human_confirmation_node"

    return "narrator_node"

def route_next_action(state: SentinelState) -> Literal["prepare_action_node", "__end__"]:
    plan = state.get("action_plan")
    idx = state.get("current_action_index", 0)
    
    if plan and idx < len(plan.actions):
        return "prepare_action_node"
    return "__end__"

# ----------------- GRAPH COMPILATION -----------------

def build_sentinel_graph():
    builder = StateGraph(SentinelState)

    builder.add_node("intent_node", intent_node)
    builder.add_node("planner_node", planner_node)
    builder.add_node("prepare_action_node", prepare_action_node)
    builder.add_node("retrieval_node", retrieval_node)
    builder.add_node("accessibility_node", accessibility_node)
    builder.add_node("risk_node", risk_node)
    builder.add_node("confidence_node", confidence_node)
    builder.add_node("decision_node", decision_node)
    builder.add_node("replacement_node", replacement_node)
    builder.add_node("human_confirmation_node", human_confirmation_node)
    builder.add_node("narrator_node", narrator_node)
    builder.add_node("trace_logger_node", trace_logger_node)

    # Edges
    builder.add_edge(START, "intent_node")
    builder.add_edge("intent_node", "planner_node")
    builder.add_edge("planner_node", "prepare_action_node")
    builder.add_edge("prepare_action_node", "retrieval_node")
    builder.add_edge("retrieval_node", "accessibility_node")
    builder.add_edge("accessibility_node", "risk_node")
    builder.add_edge("risk_node", "confidence_node")
    builder.add_edge("confidence_node", "decision_node")

    # Conditional branching from Decision
    builder.add_conditional_edges(
        "decision_node",
        route_after_decision,
        {
            "replacement_node": "replacement_node",
            "human_confirmation_node": "human_confirmation_node",
            "narrator_node": "narrator_node"
        }
    )

    # Replacement loops back to retrieval
    builder.add_edge("replacement_node", "retrieval_node")
    
    # Human confirmation proceeds to narration
    builder.add_edge("human_confirmation_node", "narrator_node")
    
    # Narration moves to trace logger
    builder.add_edge("narrator_node", "trace_logger_node")

    # Trace logger routes to next action or finishes
    builder.add_conditional_edges(
        "trace_logger_node",
        route_next_action,
        {
            "prepare_action_node": "prepare_action_node",
            "__end__": END
        }
    )

    return builder.compile()

sentinel_graph = build_sentinel_graph()
