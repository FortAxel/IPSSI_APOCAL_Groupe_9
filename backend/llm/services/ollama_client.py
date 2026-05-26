"""
Client Ollama — appel HTTP vers le service local + parsing du JSON renvoyé.

Le prompt force un format JSON strict. Le code essaie de récupérer le JSON
même si le LLM ajoute du texte autour (cas fréquent avec les modèles 7-8B).
"""
import json
import logging
import re
from typing import Any

import requests
from django.conf import settings

from .base import LLMClient, LLMError

logger = logging.getLogger(__name__)

# Limite de tokens en entrée pour éviter de saturer le contexte d'un Llama 8B
MAX_SOURCE_CHARS = 8000

SYSTEM_PROMPT = """Tu es un assistant pédagogique francophone spécialisé en
génération de QCM. À partir du cours fourni, tu génères exactement 10 questions
à choix multiples pour aider un étudiant à réviser.

Règles ABSOLUES :
- Exactement 10 questions.
- Chaque question a EXACTEMENT 4 options.
- Une seule bonne réponse par question, indiquée par "correct_index" (0 à 3).
- Pas de markdown, pas de balises HTML, pas d'explications hors JSON.
- Sortie = JSON STRICT et UNIQUEMENT JSON.

Format de sortie :
{
  "questions": [
    {"prompt": "...", "options": ["...","...","...","..."], "correct_index": 0},
    ... (10 entrées)
  ]
}
"""


class OllamaLLMClient(LLMClient):
    """Client HTTP minimal pour Ollama (/api/generate)."""

    def __init__(self) -> None:
        self.host = settings.OLLAMA_HOST.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.timeout = 120  # secondes

    def generate_quiz(self, source_text: str, title: str) -> list[dict]:
        prompt = self._build_prompt(source_text, title)
        raw = self._call_ollama(prompt)
        questions = self._parse_and_validate(raw)
        return questions

    # ----- internals -----

    def _build_prompt(self, source_text: str, title: str) -> str:
        truncated = source_text[:MAX_SOURCE_CHARS]
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"TITRE DU COURS : {title}\n\n"
            f"COURS :\n{truncated}\n\n"
            f"GÉNÈRE LE JSON MAINTENANT :"
        )

    def _call_ollama(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model":   self.model,
                    "prompt":  prompt,
                    "stream":  False,
                    "options": {"temperature": 0.4},  # peu de créativité, on veut du factuel
                    "format":  "json",                # demande à Ollama un mode JSON strict si supporté
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise LLMError(f"Ollama injoignable : {exc}") from exc

        data = response.json()
        raw = data.get("response", "")
        if not raw:
            raise LLMError("Ollama a renvoyé une réponse vide.")
        return raw

    def _parse_and_validate(self, raw: str) -> list[dict]:
        """Extrait le JSON, parse, et valide la structure."""
        # 1. Tente le parse direct (Ollama peut renvoyer du JSON pur en mode format=json)
        data: Any = None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # 2. Fallback : cherche un bloc { ... } dans la réponse
            match = re.search(r"\{[\s\S]*\}", raw)
            if not match:
                raise LLMError("Aucun bloc JSON trouvé dans la réponse LLM.")
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                raise LLMError(f"JSON LLM invalide : {exc}") from exc

        # 3. Validation structure
        if not isinstance(data, dict) or "questions" not in data:
            raise LLMError("Le JSON LLM ne contient pas la clé 'questions'.")

        questions = data["questions"]
        if not isinstance(questions, list):
            raise LLMError("'questions' n'est pas une liste.")

        if len(questions) != 10:
            logger.warning("LLM a renvoyé %d questions au lieu de 10", len(questions))
            # Tolérance : on tronque ou complète avec un padding minimal
            if len(questions) > 10:
                questions = questions[:10]
            else:
                raise LLMError(f"Seulement {len(questions)} questions générées (10 attendues).")

        # 4. Validation par question
        cleaned: list[dict] = []
        for i, q in enumerate(questions, start=1):
            if not isinstance(q, dict):
                raise LLMError(f"Question {i} n'est pas un objet.")
            prompt = q.get("prompt")
            options = q.get("options")
            correct_index = q.get("correct_index")

            if not isinstance(prompt, str) or not prompt.strip():
                raise LLMError(f"Question {i} : prompt manquant.")
            if not isinstance(options, list) or len(options) != 4:
                raise LLMError(f"Question {i} : il faut exactement 4 options.")
            if not all(isinstance(o, str) and o.strip() for o in options):
                raise LLMError(f"Question {i} : options invalides.")
            if not isinstance(correct_index, int) or correct_index not in (0, 1, 2, 3):
                raise LLMError(f"Question {i} : correct_index doit être 0, 1, 2 ou 3.")

            cleaned.append({
                "prompt":        prompt.strip(),
                "options":       [o.strip() for o in options],
                "correct_index": correct_index,
            })

        return cleaned
