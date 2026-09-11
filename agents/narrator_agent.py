"""
Narrator Agent for SENTINEL.
Dynamically generates human-friendly, plain-English explanations of Sentinel's decisions,
translating technical WCAG guidelines and risk policies into clear user guidance.
"""
from services.ollama_service import ollama_service
from models.schemas import (
    ActionItem,
    AccessibilityResult,
    RiskResult,
    ConfidenceResult,
    DecisionResult,
    NarrationResult
)

class NarratorAgent:
    def __init__(self):
        self.ollama = ollama_service

    def run(
        self,
        action: ActionItem,
        accessibility_res: AccessibilityResult,
        risk_res: RiskResult,
        confidence_res: ConfidenceResult,
        decision_res: DecisionResult
    ) -> NarrationResult:
        prompt = (
            f"Explain SENTINEL's supervisory decision for this action in simple, friendly, natural human language:\n\n"
            f"Action: {action.action_type} on '{action.target}' ({action.description})\n"
            f"Final Decision: {decision_res.decision}\n"
            f"Decision Reason: {decision_res.reason}\n"
            f"Accessibility Status: {accessibility_res.status} (Issue: {accessibility_res.issue}, Alt: {accessibility_res.alternative})\n"
            f"Risk Level: {risk_res.risk_level} (Impact: {risk_res.impact})\n"
            f"Confidence: {confidence_res.confidence_percentage}\n"
            f"Citations: {', '.join(decision_res.citations) if decision_res.citations else 'None'}\n\n"
            f"Provide:\n"
            f"- explanation: 2 to 3 concise, clear sentences explaining what Sentinel checked, why it decided {decision_res.decision}, and any accessibility or safety principles involved.\n"
            f"- recommendation: 1 actionable sentence telling the user what will happen next or what they need to do."
        )
        system_instruction = (
            "You are the SENTINEL Narrator Agent. You communicate AI safety and accessibility findings "
            "with warmth, clarity, and precision, avoiding confusing jargon."
        )
        try:
            return self.ollama.generate_structured(
                prompt=prompt,
                schema_class=NarrationResult,
                system=system_instruction
            )
        except Exception:
            # Fallback narration if LLM takes too long or fails
            return NarrationResult(
                explanation=f"SENTINEL evaluated '{action.target}' and determined a decision of {decision_res.decision}. {decision_res.reason}",
                recommendation="Please review the proposed action and confirmation options above."
            )

narrator_agent = NarratorAgent()
