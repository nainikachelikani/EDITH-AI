"""
Knowledge Loader for SENTINEL.
Loads structured accessibility documents from data/accessibility_knowledge.json.
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from config.settings import settings
from models.schemas import RetrievedDocument

def load_accessibility_knowledge(file_path: str = settings.storage.knowledge_path) -> List[Dict[str, Any]]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Accessibility knowledge base not found at: {file_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("accessibility_knowledge.json must be a JSON array of documents.")
    
    return data
