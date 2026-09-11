"""
LangGraph State definition for SENTINEL.
Represents the shared mutable state passed across all workflow nodes.
"""
from typing import TypedDict, Optional, List, Dict, Any
from models.schemas import (
    IntentResult,
    ActionPlan,
    ActionItem,
    RetrievedDocument,
    AccessibilityResult,
    RiskResult,
    ConfidenceResult,
    DecisionResult,
    NarrationResult
)

class SentinelState(TypedDict, total=False):
    # Workflow metadata
    user_request: str
    workflow_id: str
    domain: str
    
    # Intent & Plan
    intent: Optional[IntentResult]
    action_plan: Optional[ActionPlan]
    
    # Action iteration loop
    current_action_index: int
    current_action: Optional[ActionItem]
    replacement_attempt_count: int
    
    # Dynamic Per-Action analysis state (reset for every action)
    retrieved_documents: List[RetrievedDocument]
    accessibility_result: Optional[AccessibilityResult]
    risk_result: Optional[RiskResult]
    confidence_result: Optional[ConfidenceResult]
    decision_result: Optional[DecisionResult]
    narration: Optional[NarrationResult]
    
    # Human in the loop state
    requires_confirmation: bool
    human_confirmation_status: Optional[str] # PENDING_CONFIRMATION, HUMAN_AUTHORIZED, CANCELLED, HUMAN_OVERRIDE
    
    # Accumulated results across actions
    action_evaluations: List[Dict[str, Any]]
    
    # Observability & MCP Tool Invocations
    mcp_tool_calls: List[Dict[str, Any]]
    trace_events: List[Dict[str, Any]]
    
    # Overall error if any
    error: Optional[str]
