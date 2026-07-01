# Note de décision MoSCoW — Perturbations J3 & J3-bis

**Équipe 9** · 01/07/2026 · v1.0 · PO : Amine MAHI

---

## Contexte

- **P3 · J3 (mercredi 10h00)** : vulnérabilité critique prompt injection OWASP LLM-01 — le sponsor refuse la livraison MVP sans correctif.
- **P4 · J3-bis (mercredi 14h00)** : demande SAR RGPD Art. 15 (Hugo Petit) — réponse sous 48 h pour démontrer la conformité du POC.

## Décision

| | MoSCoW | US |
|---|--------|-----|
| Sécurisation LLM (prompt injection) | **MUST** | US-24 |
| Export données RGPD  | **MUST** | US-12 |

## Pourquoi

- **J3 en MUST** : exigence non-fonctionnelle critique bloquante pour la Release 1 (17h45). Sans patch, pas de MVP validé par le sponsor.
- **J3-bis en MUST** : le sponsor exige une réponse sous 48 h ; l'export automatisé et l'audit trail SAR sont des preuves de conformité attendues à la livraison MVP.

## Contrepartie

- Repousse US-08. Cependant la marge prévue pour ces perturbations nous permettent d'integrer l'us 10 dans la release 1
- Capacité mercredi matin entièrement dédiée : sécurité et conformité RGPD.

## Validation PO

Proposé par l'équipe 9
