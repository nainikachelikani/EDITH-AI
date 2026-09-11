"""
Retriever Module for SENTINEL RAG.
Encapsulates semantic search queries against ChromaDB, returns validated RetrievedDocument objects.
"""
from typing import List, Optional
from rag.vector_store import vector_store
from models.schemas import RetrievedDocument

class SentinelRetriever:
    def __init__(self):
        self.store = vector_store

    def retrieve(self, query_text: str, top_k: Optional[int] = None) -> List[RetrievedDocument]:
        """
        Performs semantic vector search across the accessibility knowledge base.
        Returns ranked list of documents with similarity scores, references, and alternatives.
        """
        if not query_text or not query_text.strip():
            return []
        
        return self.store.query(query_text=query_text.strip(), top_k=top_k)

retriever = SentinelRetriever()
