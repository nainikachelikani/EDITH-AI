"""
Pydantic Schemas for SENTINEL.
Provides strict validation for structured inputs and outputs across all agents.
"""
from typing import List, Optional, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, field_validator

# Agent 1: Intent
class IntentResult(BaseModel):
    goal: str = Field(description="The primary user objective")
    domain: str = Field(default="general", description="Application domain (e.g. education, enterprise, healthcare)")
    constraints: List[str] = Field(default_factory=list, description="Any identified user or system constraints")
    requires_action: bool = Field(default=True, description="Whether this request requires computer action execution")

    @field_validator("constraints", mode="before")
    @classmethod
    def normalize_constraints(cls, v):
        if isinstance(v, str):
            return [v.strip()] if v.strip() else []
        return v or []

# Agent 2: Action Planner
class ActionItem(BaseModel):
    id: str = Field(description="Unique action ID, e.g. act_1")
    action_type: str = Field(description="Action verb/type e.g. click, navigate, upload, drag, delete, type, select")
    target: str = Field(description="Target UI element or system object")
    description: str = Field(description="Detailed description of what the action does and how it interacts")
    reversible: bool = Field(default=True, description="Whether this action can be undone")
    data_sensitivity: str = Field(default="low", description="Sensitivity of data involved: low, medium, high, critical")

class ActionPlan(BaseModel):
    goal: str = Field(description="The overall goal being achieved")
    actions: List[ActionItem] = Field(description="Sequential list of actions to accomplish the goal")

    @field_validator("actions", mode="before")
    @classmethod
    def normalize_actions(cls, v):
        if isinstance(v, dict):
            return [v]
        return v or []

# RAG Document Schema
class RetrievedDocument(BaseModel):
    id: str
    title: str
    reference: str
    category: str
    content: str
    relevance_score: float = Field(default=0.0, description="Similarity score between 0.0 and 1.0")
    recommended_alternatives: List[str] = Field(default_factory=list)

# Agent 3: Accessibility
class AccessibilityResult(BaseModel):
    status: Literal["ACCESSIBLE", "FRAGILE", "UNKNOWN"] = Field(description="Accessibility status")
    issue: str = Field(default="None", description="Summary of barrier detected or None")
    reason: str = Field(description="Detailed explanation referencing accessibility principles")
    alternative: str = Field(default="", description="Accessible alternative method or interaction if fragile")
    citations: List[str] = Field(default_factory=list, description="Referenced guidelines e.g. WCAG 2.5.7")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in this accessibility assessment")

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if any(k in v_upper for k in ["INACCESSIBLE", "BARRIER", "FAIL", "FRAGILE", "NON_COMPLIANT"]):
                return "FRAGILE"
            elif any(k in v_upper for k in ["ACCESSIBLE", "PASS", "COMPLIANT"]):
                return "ACCESSIBLE"
            elif any(k in v_upper for k in ["UNKNOWN", "UNCERTAIN", "AMBIGUOUS"]):
                return "UNKNOWN"
        return v

    @field_validator("citations", mode="before")
    @classmethod
    def normalize_citations(cls, v):
        if isinstance(v, str):
            return [v.strip()] if v.strip() else []
        return v or []

    @field_validator("confidence", mode="before")
    @classmethod
    def clamp_confidence(cls, v):
        try:
            val = float(v)
            if val > 1.0 and val <= 100.0:
                val = val / 100.0
            return max(0.0, min(1.0, val))
        except Exception:
            return 0.5

# Agent 4: Risk
class RiskResult(BaseModel):
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(description="Assessed risk level")
    impact: str = Field(description="Potential impact on user data or system state")
    reversible: bool = Field(default=True, description="Whether action is reversible")
    requires_confirmation: bool = Field(default=False, description="Whether policy or impact dictates human sign-off")
    applicable_policies: List[str] = Field(default_factory=list, description="IDs of applicable safety policies")
    reason: str = Field(description="Detailed rationale for the risk level")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in this risk assessment")

    @field_validator("risk_level", mode="before")
    @classmethod
    def normalize_risk(cls, v):
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if any(k in v_upper for k in ["CRITICAL", "EXTREME", "DESTRUCTIVE"]):
                return "CRITICAL"
            elif any(k in v_upper for k in ["HIGH", "SEVERE"]):
                return "HIGH"
            elif any(k in v_upper for k in ["MEDIUM", "MODERATE"]):
                return "MEDIUM"
            elif any(k in v_upper for k in ["LOW", "SAFE", "MINIMAL"]):
                return "LOW"
        return v

    @field_validator("applicable_policies", mode="before")
    @classmethod
    def normalize_policies(cls, v):
        if isinstance(v, str):
            return [v.strip()] if v.strip() else []
        return v or []

    @field_validator("confidence", mode="before")
    @classmethod
    def clamp_risk_confidence(cls, v):
        try:
            val = float(v)
            if val > 1.0 and val <= 100.0:
                val = val / 100.0
            return max(0.0, min(1.0, val))
        except Exception:
            return 0.5

# Agent 5: Confidence
class ConfidenceResult(BaseModel):
    overall_confidence: float = Field(ge=0.0, le=1.0, description="Normalized score 0.0 to 1.0")
    confidence_percentage: str = Field(description="e.g. '84%'")
    factors: Dict[str, float] = Field(description="Breakdown of individual factors")
    rationale: str = Field(description="Explanation of how confidence was determined")

# Agent 6: Decision
class DecisionResult(BaseModel):
    decision: Literal["APPROVE", "REPLACE", "BLOCK", "ESCALATE"] = Field(description="Final decision")
    requires_human_confirmation: bool = Field(default=False)
    human_confirmation_status: Optional[str] = None
    reason: str = Field(description="Transparent reason for the decision")
    recommended_alternative: Optional[str] = None
    citations: List[str] = Field(default_factory=list)

# Agent 7: Narrator
class NarrationResult(BaseModel):
    explanation: str = Field(description="Human-friendly, empathetic plain-English summary of what Sentinel did and why")
    recommendation: str = Field(description="Clear next steps for the user")

# Observability Trace Event
class TraceEvent(BaseModel):
    trace_id: str
    timestamp: str
    workflow_id: str
    agent_name: str
    input_summary: Dict[str, Any]
    output_summary: Dict[str, Any]
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: Optional[Dict[str, Any]] = None
    decision: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0
