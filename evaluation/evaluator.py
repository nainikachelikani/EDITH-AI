"""
Evaluator for SENTINEL.
Runs test cases from evaluation/gold_set.json against the real multi-agent pipeline
and computes accuracy, citation rate, escalation rate, and execution timings.
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from agents.intent_agent import intent_agent
from agents.action_planner import action_planner
from agents.accessibility_agent import accessibility_agent
from agents.risk_agent import risk_agent
from agents.confidence_agent import confidence_agent
from agents.decision_agent import decision_agent
from sentinel_mcp.tools import retrieve_accessibility_guidance, get_safety_policy
from models.schemas import RetrievedDocument

class SentinelEvaluator:
    def __init__(self, gold_set_path: str = "evaluation/gold_set.json"):
        self.gold_set_path = Path(gold_set_path)

    def load_test_cases(self) -> List[Dict[str, Any]]:
        with open(self.gold_set_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        user_req = case["user_request"]
        expected = case["expected_properties"]

        # 1. Intent & Action Planning
        intent = intent_agent.run(user_req)
        plan = action_planner.run(intent)

        # Evaluate primary action
        primary_action = plan.actions[0] if plan.actions else None
        if not primary_action:
            return {
                "id": case["id"],
                "passed": False,
                "error": "No action generated",
                "execution_time_ms": (time.time() - start_time) * 1000
            }

        # 2. RAG Retrieval via MCP
        query = f"{primary_action.action_type} {primary_action.target} {primary_action.description}"
        mcp_rag = retrieve_accessibility_guidance(query=query, top_k=3)
        docs = [RetrievedDocument(**d) for d in mcp_rag.get("documents", [])]

        # 3. Accessibility & Risk
        acc_res = accessibility_agent.run(primary_action, docs)
        pol_ctx = get_safety_policy(primary_action.action_type, primary_action.target, primary_action.description)
        risk_res = risk_agent.run(primary_action, pol_ctx)

        # 4. Confidence & Decision
        conf_res = confidence_agent.calculate(docs, acc_res, risk_res)
        dec_res = decision_agent.run(primary_action, acc_res, risk_res, conf_res, pol_ctx)

        exec_ms = round((time.time() - start_time) * 1000, 2)

        # Validation Checks
        acc_match = acc_res.status == expected.get("expected_accessibility_status")
        risk_match = risk_res.risk_level in expected.get("expected_risk_range", [risk_res.risk_level])
        decision_match = dec_res.decision == expected.get("expected_decision")
        has_citations = len(dec_res.citations) > 0 or acc_res.status == "ACCESSIBLE"

        passed = decision_match or (acc_match and risk_match)

        return {
            "id": case["id"],
            "user_request": user_req,
            "passed": passed,
            "actual_decision": dec_res.decision,
            "expected_decision": expected.get("expected_decision"),
            "actual_accessibility": acc_res.status,
            "expected_accessibility": expected.get("expected_accessibility_status"),
            "actual_risk": risk_res.risk_level,
            "expected_risk": expected.get("expected_risk_range"),
            "confidence": conf_res.overall_confidence,
            "citations": dec_res.citations,
            "has_citations": has_citations,
            "execution_time_ms": exec_ms,
            "reason": dec_res.reason
        }

    def run_all(self, max_cases: int = 5) -> Dict[str, Any]:
        """Runs evaluation over cases (defaults to first 5 for fast UI responsiveness)."""
        cases = self.load_test_cases()[:max_cases]
        results = []
        
        for case in cases:
            res = self.evaluate_case(case)
            results.append(res)

        total = len(results)
        passed_count = sum(1 for r in results if r["passed"])
        dec_acc = round(sum(1 for r in results if r["actual_decision"] == r["expected_decision"]) / max(1, total) * 100, 1)
        acc_acc = round(sum(1 for r in results if r["actual_accessibility"] == r["expected_accessibility"]) / max(1, total) * 100, 1)
        risk_acc = round(sum(1 for r in results if r["actual_risk"] in r.get("expected_risk", [])) / max(1, total) * 100, 1)
        citation_rate = round(sum(1 for r in results if r["has_citations"]) / max(1, total) * 100, 1)
        escalation_rate = round(sum(1 for r in results if r["actual_decision"] == "ESCALATE") / max(1, total) * 100, 1)
        avg_conf = round(sum(r["confidence"] for r in results) / max(1, total) * 100, 1)
        avg_time = round(sum(r["execution_time_ms"] for r in results) / max(1, total), 1)

        return {
            "total_tests": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "decision_accuracy": f"{dec_acc}%",
            "accessibility_accuracy": f"{acc_acc}%",
            "risk_accuracy": f"{risk_acc}%",
            "citation_validity_rate": f"{citation_rate}%",
            "escalation_rate": f"{escalation_rate}%",
            "average_confidence": f"{avg_conf}%",
            "average_execution_time_ms": avg_time,
            "case_results": results
        }

evaluator = SentinelEvaluator()

if __name__ == "__main__":
    print("Running evaluation...")
    summary = evaluator.run_all(max_cases=3)
    print(json.dumps(summary, indent=2))
