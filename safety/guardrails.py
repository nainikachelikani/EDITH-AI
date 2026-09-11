"""
Guardrails and Decision Engine for SENTINEL.
Applies configurable policy rules and confidence thresholds to determine the final action status.
"""
from typing import Dict, Any, Optional
from config.settings import settings
from models.schemas import (
    AccessibilityResult,
    RiskResult,
    ConfidenceResult,
    DecisionResult,
    ActionItem
)

class SentinelGuardrails:
    def __init__(self):
        self.approve_threshold = settings.policies.approve_threshold
        self.escalation_threshold = settings.policies.escalation_threshold

    def evaluate_decision(
        self,
        action: ActionItem,
        accessibility_res: AccessibilityResult,
        risk_res: RiskResult,
        confidence_res: ConfidenceResult,
        policy_context: Dict[str, Any]
    ) -> DecisionResult:
        """
        Determines APPROVE, REPLACE, BLOCK, or ESCALATE according to safety and accessibility rules.
        """
        conf_score = confidence_res.overall_confidence
        citations = list(set(accessibility_res.citations + [p.get("id") for p in policy_context.get("applicable_policies", []) if "id" in p]))

        # Rule 1: Escalation on low confidence or unknown accessibility/risk
        if conf_score < self.escalation_threshold or accessibility_res.status == "UNKNOWN":
            return DecisionResult(
                decision="ESCALATE",
                requires_human_confirmation=True,
                human_confirmation_status="ACTION REQUIRES HUMAN REVIEW",
                reason=f"Action ambiguity or low confidence ({confidence_res.confidence_percentage}). System requires human verification before proceeding.",
                recommended_alternative=None,
                citations=citations
            )

        # Rule 2: High or Critical Risk -> BLOCK and require explicit confirmation
        if risk_res.risk_level in ["HIGH", "CRITICAL"] or risk_res.requires_confirmation or policy_context.get("requires_confirmation"):
            policy_names = [p.get("name") for p in policy_context.get("applicable_policies", [])]
            reason_policy = f" Triggered policy: {', '.join(policy_names)}." if policy_names else ""
            return DecisionResult(
                decision="BLOCK",
                requires_human_confirmation=True,
                human_confirmation_status="PENDING_CONFIRMATION",
                reason=f"Action has {risk_res.risk_level} risk ({risk_res.impact}).{reason_policy} Execution is blocked until human confirmation is granted.",
                recommended_alternative=None,
                citations=citations
            )

        # Rule 3: Accessibility barrier detected -> REPLACE
        if accessibility_res.status == "FRAGILE":
            alt = accessibility_res.alternative or "Use standard keyboard accessible controls."
            return DecisionResult(
                decision="REPLACE",
                requires_human_confirmation=False,
                human_confirmation_status=None,
                reason=f"Accessibility barrier detected: {accessibility_res.issue}. {accessibility_res.reason}",
                recommended_alternative=alt,
                citations=citations
            )

        # Rule 4: Sufficiently safe and accessible -> APPROVE
        if conf_score >= self.approve_threshold and accessibility_res.status == "ACCESSIBLE" and risk_res.risk_level in ["LOW", "MEDIUM"]:
            return DecisionResult(
                decision="APPROVE",
                requires_human_confirmation=False,
                human_confirmation_status="ACTION AUTHORIZED",
                reason=f"Action verified accessible and sufficiently safe ({confidence_res.confidence_percentage} confidence).",
                recommended_alternative=None,
                citations=citations
            )

        # Fallback: Escalate marginal confidence
        return DecisionResult(
            decision="ESCALATE",
            requires_human_confirmation=True,
            human_confirmation_status="ACTION REQUIRES HUMAN REVIEW",
            reason=f"Marginal confidence ({confidence_res.confidence_percentage}) falls between approval ({self.approve_threshold}) and escalation ({self.escalation_threshold}) thresholds.",
            recommended_alternative=None,
            citations=citations
        )

guardrails = SentinelGuardrails()
