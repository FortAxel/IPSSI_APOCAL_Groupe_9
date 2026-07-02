# Matrice des risques — Perturbation J4

**Équipe 9** · EduTutor IA · 01/07/2026 · v1.0

---

## Méthode

- **Exposition** = Probabilité (1 faible / 2 moyenne / 3 élevée) × Impact (1 faible / 2 moyen / 3 fort).
- **Seuil prioritaire** : exposition ≥ 6 (cases rouges).
- Chaque risque prioritaire → **action préventive** estimée dans le product backlog v4.0.

## Matrice probabilité × impact

| Probabilité ↓ / Impact → | Faible (1) | Moyen (2) | Fort (3) |
|--------------------------|------------|-----------|----------|
| **Élevée (3)** | i18n bâclée **6** | Rejet RGAA État **9** | Saturation serveurs au pic **12** |
| **Moyenne (2)** | Bug affichage mineur **2** | Dette technique bloquante **6** | Coût cloud hors budget **9** |
| **Faible (1)** | Doc non traduite **1** | Départ prestataire **2** | Panne LLM fournisseur **3** |

## Détail des risques et actions préventives

| # | Risque | Cause probable | Expo. | Action préventive → backlog | Effet |
|---|--------|----------------|-------|-----------------------------|-------|
| R1 | **Saturation au pic de trafic** | Un seul nœud, LLM 3B lent, pas de cache | **12** | `[scale]` US-27 — Infra GPU + modèle 8B/cloud + autoscaling + cache Redis — **13 pts** | P↓ & I↓ |
| R2 | **Rejet accessibilité RGAA** | Contrastes, focus, alt, structure sémantique | **9** | `[a11y]` US-25 — Audit RGAA + correction 10 critères prioritaires — **8 pts** | P↓ |
| R3 | **Coût cloud hors budget** | GPU surdimensionné sans suivi | **9** | `[scale]` Budget alerte + dimensionnement par environnement + cache — **5 pts** | I↓ |
| R4 | **Internationalisation bâclée** | Textes codés en dur, pas de sélecteur langue | **6** | `[i18n]` US-26 — Externalisation react-i18next FR/EN/ES — **8 pts** | P↓ |
| R5 | **Qualité LLM insuffisante (gros cours / langues)** | Modèle 3B, contexte tronqué, JSON invalide | **6** | `[scale]` US-27 — Migration LLM 8B+ + `num_ctx` adapté — **inclus US-27** | P↓ & I↓ |
| R6 | **Panne fournisseur LLM** | Dépendance unique Ollama / un cloud | **3** | `[risk]` US-29 — Fournisseur secours + factory multi-backend — **5 pts** | I↓ |

## Synthèse pilotage

- **3 risques exposition ≥ 6** : R1, R2, R3 (+ R4 et R5 à surveiller).
- Le choix **LLM plus puissant + infra** traite conjointement R1, R5 et soutient R4 (qualité multilingue).
