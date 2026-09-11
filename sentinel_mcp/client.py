"""
FastMCP Client for SENTINEL.
Provides a clean, reliable client wrapper around FastMCP tools.
Demonstrates the explicit flow:
LangGraph Node -> SentinelMCPClient -> FastMCP Tool -> Backend Service -> Result.
Records execution timing, input arguments, output summary, and success status.
"""
import time
from typing import Dict, Any, Optional
from sentinel_mcp.tools import (
    mcp_app,
    retrieve_accessibility_guidance,
    analyze_action_context,
    get_safety_policy,
    log_sentinel_event
)

class SentinelMCPClient:
    """
    Dedicated local FastMCP Client for SENTINEL agents.
    Provides execution tracing, structured telemetry, and fallback reliability.
    """
    def __init__(self):
        self.app = mcp_app

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes an MCP tool with timing and structured telemetry.
        """
        start = time.time()
        success = True
        error_msg = None
        result_data = None

        try:
            if tool_name == "retrieve_accessibility_guidance":
                query = arguments.get("query", "")
                top_k = arguments.get("top_k", 4)
                result_data = retrieve_accessibility_guidance(query=query, top_k=top_k)
                output_summary = f"Retrieved {result_data.get('count', 0)} WCAG guidelines"
                
            elif tool_name == "analyze_action_context":
                action_type = arguments.get("action_type", "")
                target = arguments.get("target", "")
                desc = arguments.get("description", "")
                result_data = analyze_action_context(action_type=action_type, target=target, description=desc)
                output_summary = f"Modality: {result_data.get('modality')}, Potential barrier: {result_data.get('potential_barrier')}"

            elif tool_name == "get_safety_policy":
                action_type = arguments.get("action_type", "")
                target = arguments.get("target", "")
                impact_desc = arguments.get("impact_description", "")
                result_data = get_safety_policy(action_type=action_type, target=target, impact_description=impact_desc)
                output_summary = f"Matched {result_data.get('policy_count', 0)} policies, highest impact: {result_data.get('highest_impact')}"

            elif tool_name == "log_sentinel_event":
                event_data = arguments.get("event_data", {})
                result_data = log_sentinel_event(event_data=event_data)
                output_summary = f"Logged trace event {result_data.get('event_id')}"

            else:
                raise ValueError(f"Unknown MCP tool: {tool_name}")

        except Exception as e:
            success = False
            error_msg = str(e)
            result_data = {"error": error_msg}
            output_summary = f"Failed: {error_msg}"

        exec_ms = round((time.time() - start) * 1000, 2)

        return {
            "mcp_tool": tool_name,
            "input": arguments,
            "output_summary": output_summary,
            "result": result_data,
            "execution_time_ms": exec_ms,
            "success": success
        }

# Global singleton client
mcp_client = SentinelMCPClient()
