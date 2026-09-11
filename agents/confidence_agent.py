"""
Confidence Agent for SENTINEL.
Calculates transparent, multi-factor, weighted confidence score based on RAG evidence,
agent certainty, schema validity, and evidence coverage.
"""
from typing import List, Dict, Any
from config.settings import settings
from models.schemas import (
    RetrievedDocument,
    AccessibilityResult,
    RiskResult,
    ConfidenceResult
)

class ConfidenceAgent:
    def __init__(self):
        self.weights = settings.policies.weights

    def calculate(
        self,
        retrieved_docs: List[RetrievedDocument],
        accessibility_res: AccessibilityResult,
        risk_res: RiskResult,
        schema_valid: bool = True
    ) -> ConfidenceResult:
        """
        Calculates dynamic normalized confidence between 0.0 and 1.0.
        """
        # Factor 1: RAG Relevance (highest similarity score among retrieved docs)
        max_relevance = max([d.relevance_score for d in retrieved_docs], default=0.0)
        
        # Factor 2: Accessibility Agent self-reported confidence
        acc_conf = accessibility_res.confidence
        
        # Factor 3: Risk Agent self-reported confidence
        risk_conf = risk_res.confidence
        
        # Factor 4: Schema validity
        schema_score = 1.0 if schema_valid else 0.4
        
        # Factor 5: Evidence Coverage (proportion of retrieved docs with meaningful similarity)
        top_k = settings.rag.top_k or 4
        strong_docs = [d for d in retrieved_docs if d.relevance_score >= settings.rag.similarity_threshold]
        coverage_score = min(1.0, len(strong_docs) / max(1, top_k))

        # Weight retrieval from configuration
        w_rag = self.weights.get("rag_relevance", 0.25)
        w_acc = self.weights.get("accessibility", 0.25)
        w_risk = self.weights.get("risk", 0.20)
        w_schema = self.weights.get("schema_validity", 0.15)
        w_cov = self.weights.get("evidence_coverage", 0.15)

        total_weight = w_rag + w_acc + w_risk + w_schema + w_cov
        weighted_sum = (
            (max_relevance * w_rag) +
            (acc_conf * w_acc) +
            (risk_conf * w_risk) +
            (schema_score * w_schema) +
            (coverage_score * w_cov)
        )
        
        normalized = max(0.0, min(1.0, weighted_sum / max(0.01, total_weight)))
        percent_str = f"{int(round(normalized * 100))}%"

        factors = {
            "rag_max_relevance": round(max_relevance, 3),
            "accessibility_confidence": round(acc_conf, 3),
            "risk_confidence": round(risk_conf, 3),
            "schema_validity": round(schema_score, 3),
            "evidence_coverage": round(coverage_score, 3)
        }

        rationale = (
            f"Overall confidence of {percent_str} computed from RAG relevance ({factors['rag_max_relevance']}), "
            f"accessibility certainty ({factors['accessibility_confidence']}), risk certainty ({factors['risk_confidence']}), "
            f"and evidence coverage ({len(strong_docs)}/{top_k} documents)."
        )

        return ConfidenceResult(
            overall_confidence=round(normalized, 4),
            confidence_percentage=percent_str,
            factors=factors,
            rationale=rationale
        )

confidence_agent = ConfidenceAgent()
