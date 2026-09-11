"""
FastMCP Server for SENTINEL.
Exposes MCP tools via standard stdio / SSE interface.
"""
from mcp.tools import mcp_app

def run_server():
    """Runs the FastMCP server."""
    mcp_app.run()

if __name__ == "__main__":
    run_server()
