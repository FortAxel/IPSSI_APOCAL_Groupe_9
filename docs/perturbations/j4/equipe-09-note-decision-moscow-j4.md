# Note de décision MoSCoW — Perturbation J4

**Équipe 9** · 01/07/2026 · v1.0 · PO : Amine MAHI

---

## Contexte

- **P5 · J4 (jeudi)** : passage à l'échelle national — l'État veut EduTutor comme plateforme de référence (RGAA obligatoire), levée de fonds, internationalisation.
- **Exigences non négociables** : accessibilité (RGAA), i18n (UI + LLM), scalabilité / résilience.
- **Contrainte sponsor** : pas de code bricolé — artefacts à jour, risques identifiés, pilotage (burndown / burnup).

## Décision

| Exigence | MoSCoW | Sprint | US |
|----------|--------|--------|-----|
| Accessibilité RGAA (parcours étudiant F1–F6) | **MUST** | S6 | US-25 |
| Internationalisation UI (fichiers de langue FR / EN / ES) | **MUST** | S6 | US-26 |
| Scalabilité infra + **modèle LLM plus puissant** | **MUST** | S7 | US-27 |
| Paramètre langue du LLM à la volée | **SHOULD** | S7 | US-28 |
| Fournisseur LLM de secours (résilience) | **COULD** | S7 | US-29 |
| PoC bonus (1 axe technique) | **COULD** | S6 ou S7 | — |

## Choix stratégique scalabilité — LLM plus puissant

Pour l'axe **scalabilité**, l'équipe 9 retient une approche couplée **infra + modèle** :

1. **Montée en gamme du modèle LLM** (ex. `llama3.1:8b` on-premise GPU, ou fournisseur cloud type Groq / Mistral en production) plutôt que de conserver le `llama3.2:3b` sous charge nationale.
2. **Dimensionnement infra conséquent** : instances GPU / workers LLM dédiés, cache, réplicas lecture BDD, autoscaling des services stateless — budget rendu possible par la levée de fonds.

**Pourquoi ce choix :**

- Un modèle plus puissant **analyse plus vite** les gros cours (PDF longs, textes collés > 30 000 caractères) et réduit les timeouts / échecs de validation JSON observés en MVP.
- **Meilleure précision** pédagogique et **meilleure tenue multilingue** (génération QCM dans la langue de l'élève) — prérequis pour l'i18n et la qualité attendue par l'État.
- L'augmentation de coût infra est **anticipée et assumée** ; optimiser uniquement le horizontal scaling avec un petit modèle local ne répond pas au besoin métier (qualité + langues + volume).

→ Décision formalisée dans `docs/adr/equipe-09-scalabilite-llm-adr-v1.0.md`.

## Pourquoi (MoSCoW)

- **RGAA en MUST** : condition d'adoption par l'État (service public).
- **i18n UI en MUST** : levée de fonds = expansion internationale ; textes ne doivent plus être codés en dur.
- **Scale + LLM en MUST** : pics de trafic nationaux + cours volumineux ; le 3B ne tient pas la charge qualitative.
- **Langue LLM en SHOULD** : dépend de l'i18n UI ; livrable S7 si capacité.
- **Fallback LLM en COULD** : réduit l'impact d'une panne fournisseur (risque matrice J4).

## Contrepartie

- Release 2 (post-MVP) : les MUST J4 absorbent les sprints 6 et 7.
- US enseignant (US-21 / US-22) et SHOULD catalogue (timer, etc.) restent en **SHOULD / COULD** — report après conformité État.

## Validation PO

Proposé par l'équipe 9
