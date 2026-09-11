"""
Trace Service for SENTINEL.
Records and queries structured execution traces in storage/traces/sentinel_traces.jsonl.
Provides real execution timing, UUIDs, and tool invocation records.
"""
import os
import json
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from config.settings import settings

class TraceService:
    def __init__(self):
        self.trace_file = Path(settings.storage.trace_path)
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.trace_file.exists():
            self.trace_file.touch()

    def log_event(
        self,
        workflow_id: str,
        agent_name: str,
        input_summary: Dict[str, Any],
        output_summary: Dict[str, Any],
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        retrieved_documents: Optional[List[Dict[str, Any]]] = None,
        confidence: Optional[Dict[str, Any]] = None,
        decision: Optional[Dict[str, Any]] = None,
        execution_time_ms: float = 0.0
    ) -> Dict[str, Any]:
        """Logs an immutable, structured trace event."""
        trace_id = f"tr_{uuid.uuid4().hex[:12]}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        event = {
            "trace_id": trace_id,
            "timestamp": timestamp,
            "workflow_id": workflow_id,
            "agent_name": agent_name,
            "execution_time_ms": round(execution_time_ms, 2),
            "input_summary": input_summary,
            "output_summary": output_summary,
            "tool_calls": tool_calls or [],
            "retrieved_documents": retrieved_documents or [],
            "confidence": confidence,
            "decision": decision
        }

        try:
            with open(self.trace_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            # Fallback error logging without crashing
            print(f"[TraceService Error] Failed to write trace: {e}")

        return event

    def get_recent_traces(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Reads recent trace lines from JSONL file in reverse chronological order."""
        if not self.trace_file.exists():
            return []
        
        traces = []
        try:
            with open(self.trace_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines[-limit:]):
                    line = line.strip()
                    if line:
                        try:
                            traces.append(json.loads(line))
                        except Exception:
                            continue
        except Exception as e:
            print(f"[TraceService Error] Failed to read traces: {e}")
        return traces

    def get_workflows_summary(self) -> List[Dict[str, Any]]:
        """Groups recent traces by workflow_id for easy inspection."""
        traces = self.get_recent_traces(limit=200)
        workflows: Dict[str, Dict[str, Any]] = {}

        for tr in traces:
            wid = tr.get("workflow_id", "unknown")
            if wid not in workflows:
                workflows[wid] = {
                    "workflow_id": wid,
                    "first_seen": tr.get("timestamp"),
                    "events_count": 0,
                    "agents": set(),
                    "final_decision": None,
                    "total_execution_ms": 0.0,
                    "events": []
                }
            workflows[wid]["events_count"] += 1
            workflows[wid]["agents"].add(tr.get("agent_name", "unknown"))
            workflows[wid]["total_execution_ms"] += tr.get("execution_time_ms", 0.0)
            workflows[wid]["events"].append(tr)
            
            # Record final decision if present
            if tr.get("decision") and not workflows[wid]["final_decision"]:
                workflows[wid]["final_decision"] = tr.get("decision", {}).get("decision")

        # Convert sets to lists
        result = []
        for w in workflows.values():
            w["agents"] = list(w["agents"])
            w["total_execution_ms"] = round(w["total_execution_ms"], 2)
            result.append(w)
        return result

trace_service = TraceService()
