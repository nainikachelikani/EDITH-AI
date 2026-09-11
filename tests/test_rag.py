"""
Unit tests for ChromaDB RAG and Knowledge Base retrieval.
"""
import pytest
from rag.knowledge_loader import load_accessibility_knowledge
from rag.retriever import retriever
from rag.vector_store import vector_store

def test_knowledge_base_loaded():
    docs = load_accessibility_knowledge()
    assert len(docs) >= 15, "Knowledge base must contain at least 15 WCAG documents"
    for d in docs:
        assert "id" in d
        assert "title" in d
        assert "reference" in d
        assert "content" in d
        assert "recommended_alternatives" in d

def test_vector_store_initialized():
    status = vector_store.get_status()
    assert status["document_count"] >= 15
    assert status["collection_name"] == "sentinel_accessibility_knowledge"

def test_semantic_retrieval_drag():
    docs = retriever.retrieve("drag and drop files", top_k=2)
    assert len(docs) > 0
    # Must retrieve dragging movement or drag-and-drop guideline
    matched_refs = [d.reference for d in docs]
    assert any("2.5.7" in r for r in matched_refs), f"Expected WCAG 2.5.7 in {matched_refs}"

def test_semantic_retrieval_keyboard():
    docs = retriever.retrieve("keyboard focus indicator visible", top_k=2)
    assert len(docs) > 0
    matched_refs = [d.reference for d in docs]
    assert any("2.4.7" in r or "2.1.1" in r or "2.4.3" in r for r in matched_refs)

def test_semantic_retrieval_destructive():
    docs = retriever.retrieve("permanently delete user data without confirmation", top_k=2)
    assert len(docs) > 0
    matched_refs = [d.reference for d in docs]
    assert any("3.3.4" in r for r in matched_refs)
