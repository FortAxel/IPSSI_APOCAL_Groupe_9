# Note de décision MoSCoW — Perturbation J4

**Équipe 9** · 01/07/2026 · v1.0 · PO : Amine MAHI

> Copie de référence — document source : [`docs/perturbations/j4/equipe-09-note-decision-moscow-j4.md`](../perturbations/j4/equipe-09-note-decision-moscow-j4.md)

---

## Contexte

**P5 · J4** : succès national, adoption État (RGAA), levée de fonds, i18n, scalabilité.

## Décision

| Exigence | MoSCoW | Sprint | US |
|----------|--------|--------|-----|
| Accessibilité RGAA | **MUST** | S6 | US-25 |
| i18n interface | **MUST** | S6 | US-26 |
| Scalabilité + LLM plus puissant | **MUST** | S7 | US-27 |
| Langue LLM à la volée | **SHOULD** | S7 | US-28 |
| Fournisseur LLM de secours | **COULD** | S7 | US-29 |

## Choix scalabilité

Montée en gamme **modèle LLM** (8B+ / cloud) **et** **infra dimensionnée** (GPU, autoscaling, cache) — voir ADR scalabilité LLM.

## Validation PO

Proposé par l'équipe 9
