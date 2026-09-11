"""
ChromaDB Vector Store for SENTINEL.
Manages persistent collection of accessibility knowledge documents.
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from config.settings import settings
from rag.embeddings import embedding_function
from rag.knowledge_loader import load_accessibility_knowledge
from models.schemas import RetrievedDocument

COLLECTION_NAME = "sentinel_accessibility_knowledge"

class SentinelVectorStore:
    def __init__(self):
        self.chroma_path = settings.storage.chroma_path
        os.makedirs(self.chroma_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self._get_or_create_collection()
        self._ensure_knowledge_indexed()

    def _get_or_create_collection(self):
        return self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def _ensure_knowledge_indexed(self):
        count = self.collection.count()
        if count == 0:
            self.index_knowledge_documents()

    def index_knowledge_documents(self):
        docs = load_accessibility_knowledge()
        ids = []
        documents = []
        metadatas = []

        for item in docs:
            ids.append(item["id"])
            # Format enriched document text for semantic search
            doc_text = (
                f"Title: {item['title']}\n"
                f"Reference: {item['reference']}\n"
                f"Category: {item['category']}\n"
                f"Content: {item['content']}\n"
                f"Problem Patterns: {', '.join(item.get('problem_patterns', []))}\n"
                f"Recommended Alternatives: {'; '.join(item.get('recommended_alternatives', []))}"
            )
            documents.append(doc_text)
            
            # Metadata must be primitives
            metadatas.append({
                "id": item["id"],
                "title": item["title"],
                "reference": item["reference"],
                "category": item["category"],
                "content": item["content"],
                "alternatives_json": json.dumps(item.get("recommended_alternatives", []))
            })

        # Generate embeddings
        embeddings = embedding_function.embed_documents(documents)

        # Upsert into ChromaDB
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, query_text: str, top_k: Optional[int] = None) -> List[RetrievedDocument]:
        k = top_k or settings.rag.top_k
        query_embedding = embedding_function.embed_query(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["metadatas", "documents", "distances"]
        )

        retrieved_docs: List[RetrievedDocument] = []
        if not results or not results["ids"] or len(results["ids"][0]) == 0:
            return retrieved_docs

        ids = results["ids"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for doc_id, meta, dist in zip(ids, metadatas, distances):
            # In cosine space, distance is 1 - cosine_similarity
            similarity = max(0.0, min(1.0, 1.0 - float(dist)))
            alts = []
            if "alternatives_json" in meta:
                try:
                    alts = json.loads(meta["alternatives_json"])
                except Exception:
                    alts = []

            retrieved_docs.append(RetrievedDocument(
                id=doc_id,
                title=meta.get("title", ""),
                reference=meta.get("reference", ""),
                category=meta.get("category", ""),
                content=meta.get("content", ""),
                relevance_score=round(similarity, 4),
                recommended_alternatives=alts
            ))

        return retrieved_docs

    def get_status(self) -> Dict[str, Any]:
        return {
            "collection_name": COLLECTION_NAME,
            "document_count": self.collection.count(),
            "storage_path": self.chroma_path,
            "embedding_provider": embedding_function.get_status()
        }

vector_store = SentinelVectorStore()
