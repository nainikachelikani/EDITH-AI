"""
System Service for SENTINEL.
Aggregates health, connectivity, model, storage, and tool metrics across all components.
"""
from typing import Dict, Any
from config.settings import settings
from services.ollama_service import ollama_service
from rag.vector_store import vector_store

class SystemService:
    def get_full_system_status(self) -> Dict[str, Any]:
        # 1. Ollama status
        ollama_status = ollama_service.check_health()
        
        # 2. ChromaDB status
        try:
            chroma_status = vector_store.get_status()
        except Exception as e:
            chroma_status = {"error": str(e), "document_count": 0}

        # 3. MCP status
        mcp_status = {
            "status": "ready",
            "framework": "FastMCP",
            "registered_tools": [
                "retrieve_accessibility_guidance",
                "analyze_action_context",
                "get_safety_policy",
                "log_sentinel_event"
            ]
        }

        # 4. LangGraph status
        langgraph_status = {
            "status": "ready",
            "version": "1.2.11",
            "type": "StateGraph with Human-In-The-Loop Conditional Routing"
        }

        return {
            "app_name": settings.app.name,
            "version": settings.app.version,
            "ollama": ollama_status,
            "chromadb": chroma_status,
            "mcp": mcp_status,
            "langgraph": langgraph_status,
            "policies": {
                "approve_threshold": settings.policies.approve_threshold,
                "escalation_threshold": settings.policies.escalation_threshold,
                "max_replacement_attempts": settings.policies.max_replacement_attempts
            }
        }

system_service = SystemService()
