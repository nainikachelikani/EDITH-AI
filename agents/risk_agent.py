"""
Risk Agent for SENTINEL.
Analyzes operational safety, impact severity, reversibility, and human confirmation needs.
Integrates dynamic LLM reasoning with configurable safety policy rules.
"""
from typing import Dict, Any, List
from services.ollama_service import ollama_service
from models.schemas import ActionItem, RiskResult

class RiskAgent:
    def __init__(self):
        self.ollama = ollama_service

    def run(self, action: ActionItem, policy_context: Dict[str, Any]) -> RiskResult:
        policies = policy_context.get("applicable_policies", [])
        policy_summary = "\n".join([
            f"- Policy: {p.get('name')} (Impact: {p.get('impact_level')}, Rule: {p.get('recommendation')}) - {p.get('mitigation_instructions')}"
            for p in policies
        ]) or "No pre-configured policy matched; analyze autonomously."

        prompt = (
            f"Analyze the risk and user consequence of this computer action:\n"
            f"Action: {action.action_type}\n"
            f"Target: {action.target}\n"
            f"Description: {action.description}\n"
            f"Reported Reversibility: {action.reversible}\n"
            f"Data Sensitivity: {action.data_sensitivity}\n\n"
            f"Configured Safety Policies for this context:\n"
            f"{policy_summary}\n\n"
            f"Assess:\n"
            f"- risk_level: 'LOW' (read-only, navigation), 'MEDIUM' (draft editing, non-destructive), 'HIGH' (irrevocable submit, external broadcast), 'CRITICAL' (permanent deletion, financial transaction)\n"
            f"- impact: clear description of consequence to user data or system state\n"
            f"- reversible: boolean indicating if the operation can truly be undone\n"
            f"- requires_confirmation: boolean indicating if explicit human sign-off is mandatory\n"
            f"- applicable_policies: list of policy IDs matched\n"
            f"- reason: detailed safety justification\n"
            f"- confidence: float between 0.0 and 1.0 representing certainty"
        )
        system_instruction = (
            "You are the SENTINEL Risk Agent. You protect users from accidental data loss, irrevocable submissions, "
            "and unsafe computer operations by identifying high-impact actions that mandate human verification."
        )
        return self.ollama.generate_structured(
            prompt=prompt,
            schema_class=RiskResult,
            system=system_instruction
        )

risk_agent = RiskAgent()
