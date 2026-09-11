"""
Unit tests for LangGraph state and workflow compilation.
"""
import pytest
from graph.sentinel_graph import sentinel_graph, route_after_decision
from models.schemas import DecisionResult

def test_sentinel_graph_compiled():
    assert sentinel_graph is not None

def test_routing_after_decision_replace():
    state = {
        "decision_result": DecisionResult(
            decision="REPLACE",
            reason="Dragging barrier",
            recommended_alternative="Keyboard command"
        ),
        "replacement_attempt_count": 0
    }
    next_node = route_after_decision(state)
    assert next_node == "replacement_node"

def test_routing_after_decision_block():
    state = {
        "decision_result": DecisionResult(
            decision="BLOCK",
            requires_human_confirmation=True,
            reason="Critical risk"
        )
    }
    next_node = route_after_decision(state)
    assert next_node == "human_confirmation_node"

def test_routing_after_decision_approve():
    state = {
        "decision_result": DecisionResult(
            decision="APPROVE",
            reason="Safe and accessible"
        )
    }
    next_node = route_after_decision(state)
    assert next_node == "narrator_node"
