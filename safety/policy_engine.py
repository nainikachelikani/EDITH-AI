"""
Safety Policy Engine for SENTINEL.
Loads structured safety policies from data/safety_policy.json and matches them against
structured action properties (impact, reversibility, sensitivity).
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from config.settings import settings
from models.schemas import ActionItem

class SafetyPolicyEngine:
    def __init__(self):
        self.policy_path = settings.storage.safety_policy_path
        self._policies = self._load_policies()

    def _load_policies(self) -> List[Dict[str, Any]]:
        path = Path(self.policy_path)
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("policies", [])
        except Exception:
            return []

    def evaluate(self, action: ActionItem) -> Dict[str, Any]:
        """
        Matches action against policies based on action type, sensitivity, and reversibility.
        """
        matched = []
        requires_confirmation = False
        highest_impact = "LOW"
        recommendation = "APPROVE"
        
        impact_ranks = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        action_text = f"{action.action_type} {action.target} {action.description}".lower()

        for p in self._policies:
            conditions = p.get("applicable_conditions", {})
            cats = conditions.get("operation_categories", [])
            sensitivities = conditions.get("data_sensitivity", [])
            irreversible_only = conditions.get("irreversible_only", False)

            # Match operation category
            cat_match = any(c in action_text for c in cats)
            # Match sensitivity if specified
            sens_match = action.data_sensitivity.lower() in [s.lower() for s in sensitivities] if sensitivities else True
            # Match reversibility
            rev_match = (not action.reversible) if irreversible_only else True

            if cat_match and (sens_match or not action.reversible):
                matched.append(p)
                if p.get("requires_confirmation"):
                    requires_confirmation = True
                
                p_impact = p.get("impact_level", "LOW")
                if impact_ranks.get(p_impact, 1) > impact_ranks.get(highest_impact, 1):
                    highest_impact = p_impact
                    recommendation = p.get("policy_recommendation", "BLOCK")

        return {
            "applicable_policies": matched,
            "policy_count": len(matched),
            "requires_confirmation": requires_confirmation,
            "highest_impact": highest_impact,
            "policy_recommendation": recommendation
        }

policy_engine = SafetyPolicyEngine()
