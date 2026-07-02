# ADR-007 — Scalabilité : infra dimensionnée + modèle LLM plus puissant

- **Statut** : Proposé (Perturbation J4)
- **Date** : 2026-07-01
- **Équipe** : 9
- **Contexte** : Perturbation J4 — passage à l'échelle nationale, adoption État, levée de fonds

---

## Contexte

Après le MVP (Release 1), EduTutor fait face à :

- Des **pics de charge** (millions d'élèves potentiels).
- Des **cours volumineux** (PDF / textes longs) et une **exigence multilingue**.
- Des **échecs de génération** fréquents avec `llama3.2:3b` (JSON incomplet, options invalides, lenteur CPU).

L'alternative « uniquement autoscaling + garder le 3B » ne résout ni la qualité ni la latence LLM.

## Décision

Nous adoptons une stratégie **couplée** :

1. **Modèle LLM plus puissant** en production cible :
   - **On-premise** : `llama3.1:8b` (ou équivalent 8B) sur **GPU dédié** (workers Ollama).
   - **Cloud** (pics / secours) : fournisseur rapide type **Groq** ou **Mistral** (free tier / budget levée de fonds).
2. **Infrastructure dimensionnée en conséquence** :
   - Backend / frontend : **stateless**, autoscaling horizontal.
   - **Workers LLM** séparés du web (file d'attente Celery ou équivalent pour génération asynchrone si besoin).
   - PostgreSQL : instance managée + **réplica lecture**.
   - **Cache** (Redis) pour sessions / config / résultats fréquents.
   - **CDN** pour le frontend statique en production.
3. **Conserver** l'architecture multi-fournisseurs (`LLM_BACKEND`, factory) — le modèle puissant s'intègre sans réécriture métier.

Le **3B** reste disponible en **dev local** (postes étudiants, CI mock).

## Conséquences

### Positives

- Génération **plus rapide** sur gros cours (meilleur débit tokens/s sur GPU 8B).
- **Meilleure précision** QCM et **meilleure tenue multilingue** (prérequis i18n + État).
- Moins de retries / 502 côté validation JSON.
- Alignement avec le budget post-levée de fonds.

### Négatives

- **Coût infra** plus élevé (GPU, cloud API).
- **RGPD** : si cloud → DPA / hébergement UE à documenter (déjà anticipé en étude).
- Migration ops : déploiement Ollama GPU + variables `.env` prod.

## Alternatives envisagées

| Alternative | Rejet car |
|-------------|-----------|
| Garder 3B + scale horizontal seul | Qualité et latence LLM insuffisantes à l'échelle nationale |
| Cloud uniquement sans GPU local | Coût imprévisible ; perte souveraineté pour démos formation |
| RAG / découpage cours seul | Utile en complément mais ne remplace pas un modèle plus capable sur JSON structuré |

## Liens

- Matrice risques J4 : R1, R5
- Note MoSCoW J4
