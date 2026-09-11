"""
EDITH-AI Settings and Configuration Loader.
Loads settings from YAML files and environment variables.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

def load_yaml(filepath: Path) -> Dict[str, Any]:
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

_settings_yaml = load_yaml(BASE_DIR / "config" / "settings.yaml")
_policies_yaml = load_yaml(BASE_DIR / "config" / "policies.yaml")

class AppConfig(BaseModel):
    name: str = _settings_yaml.get("app", {}).get("name", "EDITH-AI")
    tagline: str = _settings_yaml.get("app", {}).get("tagline", "An Intelligent Accessibility and Safety Layer for AI Agents")
    version: str = _settings_yaml.get("app", {}).get("version", "1.0.0")

class OllamaConfig(BaseModel):
    base_url: str = os.getenv("OLLAMA_BASE_URL", _settings_yaml.get("ollama", {}).get("base_url", "http://localhost:11434"))
    model: str = os.getenv("OLLAMA_MODEL", _settings_yaml.get("ollama", {}).get("model", "llama3.2:latest"))
    embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", _settings_yaml.get("ollama", {}).get("embed_model", "nomic-embed-text"))
    temperature: float = float(_settings_yaml.get("ollama", {}).get("temperature", 0.1))
    timeout_seconds: int = int(_settings_yaml.get("ollama", {}).get("timeout_seconds", 60))

class StorageConfig(BaseModel):
    chroma_path: str = str(BASE_DIR / os.getenv("CHROMA_PATH", _settings_yaml.get("storage", {}).get("chroma_path", "storage/chroma")))
    trace_path: str = str(BASE_DIR / os.getenv("TRACE_PATH", _settings_yaml.get("storage", {}).get("trace_path", "storage/traces/sentinel_traces.jsonl")))
    knowledge_path: str = str(BASE_DIR / _settings_yaml.get("storage", {}).get("knowledge_path", "data/accessibility_knowledge.json"))
    safety_policy_path: str = str(BASE_DIR / _settings_yaml.get("storage", {}).get("safety_policy_path", "data/safety_policy.json"))

class RagConfig(BaseModel):
    top_k: int = int(_settings_yaml.get("rag", {}).get("top_k", 4))
    similarity_threshold: float = float(_settings_yaml.get("rag", {}).get("similarity_threshold", 0.35))

class ConfidenceWeights(BaseModel):
    rag_relevance: float = 0.25
    accessibility: float = 0.25
    risk: float = 0.20
    schema_validity: float = 0.15
    evidence_coverage: float = 0.15

class PolicyConfig(BaseModel):
    approve_threshold: float = float(_policies_yaml.get("confidence", {}).get("approve_threshold", 0.75))
    escalation_threshold: float = float(_policies_yaml.get("confidence", {}).get("escalation_threshold", 0.55))
    weights: Dict[str, float] = _policies_yaml.get("confidence", {}).get("weights", {
        "rag_relevance": 0.25,
        "accessibility": 0.25,
        "risk": 0.20,
        "schema_validity": 0.15,
        "evidence_coverage": 0.15
    })
    max_replacement_attempts: int = int(_settings_yaml.get("execution", {}).get("max_replacement_attempts", 1))

class Settings(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    rag: RagConfig = Field(default_factory=RagConfig)
    policies: PolicyConfig = Field(default_factory=PolicyConfig)

settings = Settings()
