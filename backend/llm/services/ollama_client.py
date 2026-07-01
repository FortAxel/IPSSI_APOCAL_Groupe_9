"""
Client Ollama — appel HTTP vers le service LLM LOCAL (gratuit).

[Note pédagogique] Ollama fait tourner un modèle open-source (Llama, Phi,
Mistral…) en local, sans clé API ni coût. C'est le backend par DÉFAUT du kit :
souveraineté des données + zéro coût. Sa contrepartie est la latence sur CPU
(cf. perturbation J2). Le prompt et la validation sont mutualisés dans
quiz_prompt.py et partagés avec les clients OpenAI / Claude.
"""

import requests
from django.conf import settings

from .base import LLMClient, LLMError
from .quiz_prompt import build_system_prompt, build_user_prompt, generate_quiz_validated


class OllamaLLMClient(LLMClient):
    """Client HTTP minimal pour Ollama (/api/chat avec rôles system/user)."""

    def __init__(
        self, *, model: str | None = None, host: str | None = None, timeout: int | None = None
    ) -> None:
        # Overrides éventuels (config admin en base, Lot 8) sinon valeurs .env.
        self.host = (host or settings.OLLAMA_HOST).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        # Configurable via OLLAMA_TIMEOUT (.env). Défaut 600 s : une génération
        # 8B sur CPU peut dépasser largement 120 s (cf. perturbation J2 latence).
        self.timeout = timeout or settings.OLLAMA_TIMEOUT

    def generate_quiz(
        self,
        source_text: str,
        title: str,
        *,
        nb_questions: int = 10,
        difficulty: str = "medium",
    ) -> list[dict]:
        # T-24.2 : séparation system/user via /api/chat (défense OWASP LLM-01).
        user_content = build_user_prompt(
            source_text,
            title,
            nb_questions=nb_questions,
            difficulty=difficulty,
        )
        system_prompt = build_system_prompt(nb_questions, difficulty)
        return generate_quiz_validated(
            lambda *, retry_hint=None, attempt=1: self._call_ollama_chat(
                user_content, system_prompt, retry_hint=retry_hint, attempt=attempt
            ),
            nb_questions=nb_questions,
        )

    # ----- internals -----

    def _call_ollama_chat(
        self,
        user_content: str,
        system_prompt: str,
        *,
        retry_hint: str | None = None,
        attempt: int = 1,
    ) -> str:
        if retry_hint:
            user_content = (
                f"{user_content}\n\n"
                f"⚠️ ERREUR PRÉCÉDENTE (tentative {attempt}) : {retry_hint}\n"
                "Corrige et renvoie UNIQUEMENT le JSON complet conforme aux règles."
            )
        temperature = min(0.2 + (attempt - 1) * 0.15, 0.65)
        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "seed": attempt * 7919,
                        "num_ctx": settings.OLLAMA_NUM_CTX,
                        "num_predict": settings.OLLAMA_NUM_PREDICT,
                    },
                    "format": "json",
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise LLMError(f"Ollama injoignable : {exc}") from exc

        data = response.json()
        message = data.get("message") or {}
        raw = message.get("content", "")
        if not raw:
            raise LLMError("Ollama a renvoyé une réponse vide.")
        return raw
