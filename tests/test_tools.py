"""
Unit tests for FastMCP tools in SENTINEL.
"""
import pytest
from sentinel_mcp.tools import (
    retrieve_accessibility_guidance,
    analyze_action_context,
    get_safety_policy,
    log_sentinel_event
)

def test_tool_retrieve_accessibility_guidance():
    res = retrieve_accessibility_guidance(query="keyboard navigation", top_k=2)
    assert res["success"] is True
    assert res["count"] > 0
    assert "execution_time_ms" in res
    assert len(res["documents"]) > 0

def test_tool_analyze_action_context():
    res = analyze_action_context(
        action_type="drag",
        target="file_card",
        description="Drag file into assignment dropzone"
    )
    assert res["success"] is True
    assert res["modality"] == "mouse_dependent"
    assert res["potential_barrier"] is True
    assert "WCAG 2.5.7" in res["barrier_hint"]

def test_tool_get_safety_policy():
    res = get_safety_policy(
        action_type="delete",
        target="final_exam_submission",
        impact_description="Permanently delete student submission file"
    )
    assert res["success"] is True
    assert res["policy_count"] > 0
    assert res["requires_confirmation"] is True
    assert res["highest_impact"] in ["HIGH", "CRITICAL"]

def test_tool_log_sentinel_event():
    res = log_sentinel_event({
        "workflow_id": "test_wf_99",
        "agent_name": "TestRunner",
        "test_metric": 100
    })
    assert res["success"] is True
    assert "event_id" in res
    assert "execution_time_ms" in res

def test_sentinel_mcp_client_invocations():
    from sentinel_mcp.client import mcp_client
    
    # 1. retrieve_accessibility_guidance
    r1 = mcp_client.call_tool("retrieve_accessibility_guidance", {"query": "drag and drop alternative", "top_k": 2})
    assert r1["mcp_tool"] == "retrieve_accessibility_guidance"
    assert r1["success"] is True
    assert "WCAG" in r1["output_summary"]
    assert r1["execution_time_ms"] >= 0
    
    # 2. get_safety_policy
    r2 = mcp_client.call_tool("get_safety_policy", {"action_type": "delete", "target": "user_data", "impact_description": "purge all records"})
    assert r2["mcp_tool"] == "get_safety_policy"
    assert r2["success"] is True
    assert "Matched" in r2["output_summary"]
    assert r2["execution_time_ms"] >= 0
    
    # 3. log_sentinel_event
    r3 = mcp_client.call_tool("log_sentinel_event", {"event_data": {"workflow_id": "wf_client_test", "status": "verified"}})
    assert r3["mcp_tool"] == "log_sentinel_event"
    assert r3["success"] is True
    assert "Logged trace event" in r3["output_summary"]
    assert r3["execution_time_ms"] >= 0

