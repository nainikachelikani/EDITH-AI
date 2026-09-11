"""
Decision Agent for SENTINEL.
Synthesizes accessibility assessment, risk assessment, multi-factor confidence,
and policy context into a final transparent supervisory decision.
"""
from typing import Dict, Any
from safety.guardrails import guardrails
from models.schemas import (
    ActionItem,
    AccessibilityResult,
    RiskResult,
    ConfidenceResult,
    DecisionResult
)

class DecisionAgent:
    def __init__(self):
        self.guardrails = guardrails

    def run(
        self,
        action: ActionItem,
        accessibility_res: AccessibilityResult,
        risk_res: RiskResult,
        confidence_res: ConfidenceResult,
        policy_context: Dict[str, Any]
    ) -> DecisionResult:
        return self.guardrails.evaluate_decision(
            action=action,
            accessibility_res=accessibility_res,
            risk_res=risk_res,
            confidence_res=confidence_res,
            policy_context=policy_context
        )

decision_agent = DecisionAgent()
