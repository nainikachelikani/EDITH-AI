"""
Action Planner Agent for SENTINEL.
Decomposes user goal into a sequence of granular computer action items.
"""
from typing import List
from services.ollama_service import ollama_service
from models.schemas import IntentResult, ActionPlan, ActionItem

class ActionPlannerAgent:
    def __init__(self):
        self.ollama = ollama_service

    def run(self, intent: IntentResult) -> ActionPlan:
        prompt = (
            f"Given the user goal: \"{intent.goal}\" in domain \"{intent.domain}\", "
            f"decompose it into a sequential list of 1 to 4 proposed computer actions.\n\n"
            f"Constraints: {intent.constraints}\n\n"
            f"For each action provide:\n"
            f"- id: e.g. act_1, act_2\n"
            f"- action_type: verb like click, navigate, upload, drag, delete, type, select\n"
            f"- target: specific UI element or system entity (e.g. 'assignment file', 'submit button', 'course syllabus')\n"
            f"- description: detailed operational explanation of the action\n"
            f"- reversible: boolean true if action can be undone\n"
            f"- data_sensitivity: 'low', 'medium', 'high', or 'critical'"
        )
        system_instruction = (
            "You are the SENTINEL Action Planner Agent. You convert user goals into realistic, "
            "granular computer interaction steps."
        )
        return self.ollama.generate_structured(
            prompt=prompt,
            schema_class=ActionPlan,
            system=system_instruction
        )

action_planner = ActionPlannerAgent()
