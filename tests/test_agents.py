"""
Unit tests for confidence, guardrails, and decision agents.
"""
import pytest
from models.schemas import (
    ActionItem,
    RetrievedDocument,
    AccessibilityResult,
    RiskResult
)
from agents.confidence_agent import confidence_agent
from agents.decision_agent import decision_agent

def test_confidence_calculation():
    docs = [
        RetrievedDocument(
            id="test_doc",
            title="Test Doc",
            reference="WCAG 2.1.1",
            category="keyboard",
            content="Keyboard accessibility standard",
            relevance_score=0.85
        )
    ]
    acc = AccessibilityResult(
        status="ACCESSIBLE",
        issue="None",
        reason="Standard keyboard button",
        confidence=0.9
    )
    risk = RiskResult(
        risk_level="LOW",
        impact="Read only navigation",
        reversible=True,
        requires_confirmation=False,
        reason="No data changed",
        confidence=0.9
    )
    conf = confidence_agent.calculate(docs, acc, risk)
    assert conf.overall_confidence > 0.70
    assert "%" in conf.confidence_percentage

def test_decision_replace_on_fragile():
    act = ActionItem(
        id="act_drag",
        action_type="drag",
        target="file",
        description="Drag file to upload"
    )
    acc = AccessibilityResult(
        status="FRAGILE",
        issue="Requires dragging",
        reason="No keyboard single pointer alternative",
        alternative="Use standard browse file button",
        confidence=0.85
    )
    risk = RiskResult(
        risk_level="LOW",
        impact="Upload draft",
        reason="Safe draft upload",
        confidence=0.85
    )
    rag_docs = [
        RetrievedDocument(
            id="wcag_drag",
            title="Dragging Movements",
            reference="WCAG 2.5.7",
            category="motor",
            content="Dragging alternative required",
            relevance_score=0.88,
            recommended_alternatives=["Use browse file button"]
        )
    ]
    conf = confidence_agent.calculate(rag_docs, acc, risk)
    pol_ctx = {"requires_confirmation": False, "applicable_policies": []}
    
    dec = decision_agent.run(act, acc, risk, conf, pol_ctx)
    assert dec.decision == "REPLACE"
    assert dec.recommended_alternative is not None

def test_decision_block_on_high_risk():
    act = ActionItem(
        id="act_del",
        action_type="delete",
        target="database",
        description="Permanently purge records",
        reversible=False
    )
    acc = AccessibilityResult(
        status="ACCESSIBLE",
        issue="None",
        reason="Keyboard operable button",
        confidence=0.9
    )
    risk = RiskResult(
        risk_level="CRITICAL",
        impact="Permanent data loss",
        reversible=False,
        requires_confirmation=True,
        reason="High consequence permanent data loss",
        confidence=0.95
    )
    conf = confidence_agent.calculate([], acc, risk)
    pol_ctx = {
        "requires_confirmation": True,
        "applicable_policies": [{"name": "Permanent Data Deletion Guardrail"}]
    }
    
    dec = decision_agent.run(act, acc, risk, conf, pol_ctx)
    assert dec.decision == "BLOCK"
    assert dec.requires_human_confirmation is True
