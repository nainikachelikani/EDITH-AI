"""
Intent Agent for SENTINEL.
Analyzes user request to understand objective, domain, constraints, and action need.
"""
from typing import Optional
from services.ollama_service import ollama_service
from models.schemas import IntentResult

class IntentAgent:
    def __init__(self):
        self.ollama = ollama_service

    def run(self, user_request: str) -> IntentResult:
        prompt = (
            f"Analyze this user request and determine their intended goal, domain, constraints, and if computer action is required:\n\n"
            f"User Request: \"{user_request}\"\n\n"
            f"Provide a structured response with:\n"
            f"- goal: concise summary of what user wants to accomplish\n"
            f"- domain: e.g. education, healthcare, enterprise, finance, general\n"
            f"- constraints: list of any constraints implied by the request\n"
            f"- requires_action: boolean true if this requires computer actions"
        )
        system_instruction = (
            "You are the SENTINEL Intent Agent. You accurately interpret the user's intent "
            "and extract structured objectives without bias."
        )
        return self.ollama.generate_structured(
            prompt=prompt,
            schema_class=IntentResult,
            system=system_instruction
        )

intent_agent = IntentAgent()
