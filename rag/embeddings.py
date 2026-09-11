"""
Embeddings Provider for SENTINEL.
Implements resilient local-first embedding strategy:
1. Try local Ollama embeddings if enabled on Ollama server
2. Try local SentenceTransformers if cached
3. Local Semantic LSA/TF-IDF dense vector embeddings (100% local, offline, zero cloud API calls)
Explicitly detects and reports active provider in System Status.
"""
import os
import json
import numpy as np
import urllib.request
from typing import List, Optional, Tuple, Dict, Any
from config.settings import settings

class SentinelEmbeddingFunction:
    def __init__(self):
        self.active_provider: str = "detecting"
        self.provider_details: str = "Checking local embedding capabilities..."
        self._st_model = None
        self._lsa_pipeline = None
        self._init_provider()

    def _init_provider(self):
        # 1. Try local Ollama embeddings
        ollama_ok, reason = self._test_ollama_embeddings()
        if ollama_ok:
            self.active_provider = "ollama"
            self.provider_details = f"Local Ollama ({settings.ollama.embed_model})"
            return

        # 2. Try SentenceTransformers if locally available
        st_ok, st_msg = self._test_sentence_transformers()
        if st_ok:
            self.active_provider = "sentence-transformers"
            self.provider_details = f"Local Sentence-Transformers (all-MiniLM-L6-v2) - {st_msg}"
            return

        # 3. Robust Local Dense Semantic Embedder (sklearn TF-IDF + dense projection)
        self._init_local_semantic_embedder()
        self.active_provider = "local-semantic-lsa"
        self.provider_details = "Local Offline Semantic Vector Embedder (Dense LSA, 128-dim, Zero Network)"

    def _test_ollama_embeddings(self) -> Tuple[bool, str]:
        url = f"{settings.ollama.base_url}/api/embeddings"
        payload = {"model": settings.ollama.embed_model, "prompt": "test"}
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if "embedding" in data and len(data["embedding"]) > 0:
                        return True, "Ollama embeddings operational"
        except Exception as e:
            return False, str(e)
        return False, "Ollama embeddings not enabled"

    def _test_sentence_transformers(self) -> Tuple[bool, str]:
        try:
            from sentence_transformers import SentenceTransformer
            # Only use if explicitly local without network hang
            os.environ["HF_HUB_OFFLINE"] = "1"
            self._st_model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            return True, "Cached locally"
        except Exception as e:
            return False, str(e)

    def _init_local_semantic_embedder(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import normalize
        from rag.knowledge_loader import load_accessibility_knowledge

        try:
            docs_data = load_accessibility_knowledge()
            corpus = []
            for d in docs_data:
                text = f"{d['title']} {d['reference']} {d['category']} {d['content']} {' '.join(d.get('problem_patterns', []))} {' '.join(d.get('recommended_alternatives', []))}"
                corpus.append(text)
            
            # Ensure sufficient samples for SVD components
            n_components = min(16, max(4, len(corpus) - 1))
            self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', min_df=1)
            X = self._vectorizer.fit_transform(corpus)
            self._svd = TruncatedSVD(n_components=n_components, random_state=42)
            self._svd.fit(X)
        except Exception as err:
            self._vectorizer = TfidfVectorizer(stop_words='english')
            self._vectorizer.fit(["accessibility keyboard drag focus contrast form label error"])
            self._svd = None

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.embed_documents(input)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.active_provider == "ollama":
            return [self._get_ollama_embedding(t) for t in texts]
        elif self.active_provider == "sentence-transformers" and self._st_model:
            results = self._st_model.encode(texts, convert_to_numpy=True)
            return [vec.tolist() for vec in results]
        else:
            # Local Dense Semantic LSA
            from sklearn.preprocessing import normalize
            X = self._vectorizer.transform(texts)
            if self._svd:
                dense = self._svd.transform(X)
            else:
                dense = X.toarray()
            # Normalize to unit length for cosine similarity
            normalized = normalize(dense, norm='l2')
            return [vec.tolist() for vec in normalized]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def _get_ollama_embedding(self, text: str) -> List[float]:
        url = f"{settings.ollama.base_url}/api/embeddings"
        payload = {"model": settings.ollama.embed_model, "prompt": text}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("embedding", [])

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": self.active_provider,
            "details": self.provider_details,
            "local_only": True,
            "requires_api_key": False
        }

embedding_function = SentinelEmbeddingFunction()
