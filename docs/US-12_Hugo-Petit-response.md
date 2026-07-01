# US-12 — Réponse écrite (Hugo Petit)

Résumé :

- Risque identifié : fuite inter-comptes — un utilisateur A ne doit pas pouvoir accéder aux données (cours, quiz, statistiques) d'un utilisateur B.
- Vérification automatique : ajouter des tests pytest qui créent deux comptes (A/B), puis tentent, avec le jeton d'A, d'accéder aux ressources de B (GET /api/quizzes/<id>/, POST /api/quizzes/generate/ avec course_id de B, etc.). Les endpoints doivent renvoyer 404/403/401.

Actions réalisées :

- Ajout d'un test `adversarial` dans `backend/quizzes/tests.py` qui tente l'énumération d'IDs et vérifie l'absence de fuite (404/401/403).

Recommandations complémentaires :

- S'assurer que toutes les vues utilisent des queryset filtrés par `request.user` (déjà appliqué sur `quizzes` et `generate`).
- Ajouter des tests similaires pour `courses` et autres ressources sensibles si de nouveaux endpoints sont ajoutés.
- Documenter la politique d'accès (ownership checks) dans la doc technique.

Si vous voulez, j'intègre aussi un test anti-fuite pour les endpoints `courses` et `generate`.
