"""
Ollama Service for SENTINEL.
Provides robust communication with local Ollama, structured JSON output extraction,
model availability detection, and automatic schema validation/repair.
"""
import json
import re
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List, Type, TypeVar
from pydantic import BaseModel, ValidationError
from config.settings import settings

T = TypeVar("T", bound=BaseModel)

class OllamaService:
    def __init__(self, base_url: Optional[str] = None, default_model: Optional[str] = None):
        self.base_url = (base_url or settings.ollama.base_url).rstrip("/")
        self.default_model = default_model or settings.ollama.model
        self.embed_model = settings.ollama.embed_model
        self.timeout = settings.ollama.timeout_seconds

    def check_health(self) -> Dict[str, Any]:
        """Checks if local Ollama server is running and returns available models."""
        url = f"{self.base_url}/api/tags"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    models = [m["name"] for m in data.get("models", [])]
                    return {
                        "status": "connected",
                        "available_models": models,
                        "current_model": self.default_model,
                        "model_available": self.default_model in models or any(m.startswith(self.default_model.split(":")[0]) for m in models)
                    }
        except Exception as e:
            return {
                "status": "disconnected",
                "error": str(e),
                "available_models": [],
                "current_model": self.default_model,
                "model_available": False
            }
        return {"status": "disconnected", "available_models": [], "current_model": self.default_model, "model_available": False}

    def generate(self, prompt: str, system: Optional[str] = None, model: Optional[str] = None, json_mode: bool = True) -> str:
        """Raw generation call to Ollama."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.ollama.temperature
            }
        }
        if system:
            payload["system"] = system
        if json_mode:
            payload["format"] = "json"

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"}, method="POST")
        
        last_error = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    return result.get("response", "")
            except urllib.error.HTTPError as he:
                raise RuntimeError(f"Ollama HTTP error {he.code}: {he.read().decode('utf-8')}") from he
            except Exception as e:
                last_error = e
                if attempt < 2:
                    time.sleep(1.5)
                    continue
        raise RuntimeError(f"Failed to communicate with Ollama at {self.base_url} after 3 attempts: {last_error}") from last_error

    def generate_structured(self, prompt: str, schema_class: Type[T], system: Optional[str] = None, model: Optional[str] = None, max_retries: int = 1) -> T:
        """
        Executes an LLM prompt and ensures the output strictly parses into the given Pydantic model.
        Performs JSON extraction, sanitization, and structured repair if needed.
        """
        sample_dict = {}
        for fname, finfo in schema_class.model_fields.items():
            desc = finfo.description or "value"
            sample_dict[fname] = f"<{desc}>"
        sample_json = json.dumps(sample_dict, indent=2)

        full_system = (
            f"{system or 'You are an expert AI systems assistant.'}\n"
            f"You MUST respond ONLY with a valid JSON object matching this structure:\n"
            f"{sample_json}\n"
            f"Fill in real values for the fields based on the user's input. Do NOT return schema definitions or explanations. Return only the JSON object."
        )

        for attempt in range(max_retries + 1):
            raw_output = self.generate(prompt=prompt, system=full_system, model=model, json_mode=True)
            cleaned_json = self._extract_json_substring(raw_output)

            try:
                data = json.loads(cleaned_json)
                return schema_class.model_validate(data)
            except (json.JSONDecodeError, ValidationError) as err:
                if attempt == max_retries:
                    # Attempt structured repair fallback
                    repaired = self._attempt_repair(raw_output, schema_class)
                    if repaired:
                        return repaired
                    raise ValueError(f"Failed to validate Ollama response against {schema_class.__name__}: {err}\nRaw text: {raw_output}")
                
                # Retry prompt asking for correction
                prompt = (
                    f"Your previous response failed validation:\n{err}\n\n"
                    f"Previous invalid output:\n{raw_output}\n\n"
                    f"Please correct the JSON so it strictly adheres to this structure:\n{sample_json}"
                )

        raise RuntimeError("Unreachable error in generate_structured")

    def _extract_json_substring(self, text: str) -> str:
        """Extracts the innermost or markdown-fenced JSON object string from raw LLM text."""
        text = text.strip()
        # Check for ```json ... ``` fences
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence_match:
            return fence_match.group(1).strip()
        
        # Search for first { and last }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return text[first_brace:last_brace + 1].strip()
        
        return text

    def _attempt_repair(self, text: str, schema_class: Type[T]) -> Optional[T]:
        """Heuristic fallback to extract partial fields if JSON had minor syntax flaws."""
        try:
            cleaned = self._extract_json_substring(text)
            # Remove trailing commas
            cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)
            data = json.loads(cleaned)
            return schema_class.model_validate(data)
        except Exception:
            return None

ollama_service = OllamaService()
