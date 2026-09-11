"""
Accessibility Agent for SENTINEL.
Analyzes whether a proposed computer action creates accessibility barriers for users
with visual, motor, cognitive, or speech disabilities, grounded in retrieved WCAG guidelines.
"""
from typing import List
from services.ollama_service import ollama_service
from models.schemas import ActionItem, RetrievedDocument, AccessibilityResult

class AccessibilityAgent:
    def __init__(self):
        self.ollama = ollama_service

    def run(self, action: ActionItem, retrieved_docs: List[RetrievedDocument]) -> AccessibilityResult:
        evidence_text = "\n\n".join([
            f"Guideline ID: {d.id}\nReference: {d.reference} ({d.title})\nCategory: {d.category}\nContent: {d.content}\nAlternatives: {'; '.join(d.recommended_alternatives)}"
            for d in retrieved_docs
        ])

        prompt = (
            f"Evaluate this proposed computer action for accessibility barriers:\n"
            f"Action Type: {action.action_type}\n"
            f"Target: {action.target}\n"
            f"Description: {action.description}\n\n"
            f"Retrieved Accessibility Evidence & WCAG Standards:\n"
            f"{evidence_text if evidence_text else 'No specific guidelines retrieved.'}\n\n"
            f"Determine:\n"
            f"- status: 'ACCESSIBLE' if the action provides standard, inclusive interaction; "
            f"'FRAGILE' if it creates an accessibility barrier (e.g. requires mouse drag, hover trap, unlabeled icon, tiny target, missing focus); "
            f"'UNKNOWN' if context is ambiguous or insufficient\n"
            f"- issue: concise summary of the barrier or 'None'\n"
            f"- reason: detailed analysis citing the relevant guideline and assistive technology impact\n"
            f"- alternative: accessible alternative interaction if status is FRAGILE (e.g. keyboard command, button picker), or empty\n"
            f"- citations: list of standard references cited (e.g. ['WCAG 2.5.7'])\n"
            f"- confidence: float between 0.0 and 1.0 representing certainty"
        )
        system_instruction = (
            "You are the SENTINEL Accessibility Agent. You critically evaluate proposed computer interactions "
            "against WCAG and assistive technology principles. You recommend accessible alternatives when barriers exist."
        )
        return self.ollama.generate_structured(
            prompt=prompt,
            schema_class=AccessibilityResult,
            system=system_instruction
        )

accessibility_agent = AccessibilityAgent()
