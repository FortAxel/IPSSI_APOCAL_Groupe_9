"""Factory de client LLM selon settings.LLM_BACKEND."""
from django.conf import settings

from .base import LLMClient
from .mock_client import MockLLMClient
from .ollama_client import OllamaLLMClient


def get_llm_client() -> LLMClient:
    """Renvoie le client LLM correspondant à la configuration courante."""
    backend = (settings.LLM_BACKEND or "ollama").lower()

    if backend == "mock":
        return MockLLMClient()
    if backend == "ollama":
        return OllamaLLMClient()

    raise ValueError(
        f"LLM_BACKEND inconnu : {backend}. Valeurs autorisées : 'ollama' | 'mock'."
    )
