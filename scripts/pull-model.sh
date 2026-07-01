#!/usr/bin/env bash
# ============================================================================
# pull-model.sh — Télécharge le modèle Ollama configuré dans .env
# ----------------------------------------------------------------------------
# À exécuter UNE fois après le premier `docker compose up`.
# Modèle par défaut : llama3.2:3b (~2 Go). Surcharge via OLLAMA_MODEL dans .env.
# ============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODEL="llama3.2:3b"
if [ -f .env ]; then
  MODEL="$(sed -n 's/^[[:space:]]*OLLAMA_MODEL[[:space:]]*=[[:space:]]*//p' .env | head -n1)"
  MODEL="${MODEL:-llama3.2:3b}"
fi

CONTAINER="${OLLAMA_CONTAINER:-apocalipssi-2026-ollama}"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "❌ Conteneur Ollama '${CONTAINER}' non démarré."
    echo "   Lancez d'abord : docker compose up -d"
    exit 1
fi

echo "⏳ Téléchargement du modèle ${MODEL} dans ${CONTAINER}..."
echo "   Cela prend généralement 3 à 10 minutes selon votre connexion."
echo ""

docker exec "${CONTAINER}" ollama pull "${MODEL}"

echo ""
echo "✅ Modèle ${MODEL} téléchargé avec succès."
echo ""
echo "🧪 Test rapide :"
docker exec "${CONTAINER}" ollama list
