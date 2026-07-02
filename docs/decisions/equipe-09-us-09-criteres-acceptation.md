# Note — Critères d'acceptation US-09 (Niveaux de difficulté et nombre variable de questions)

**Équipe 9** · 1er juillet 2026 · v1.0 · MoSCoW : SHOULD

---

## 1. Contexte

L'US-09 permet à l'utilisateur de paramétrer la génération de quiz avec un
niveau de difficulté (facile, moyen, difficile) et un nombre de questions
(5 à 20) avant de lancer la génération. Issue du catalogue d'idées MVP2
([§4 « Niveaux de difficulté »](08-mvp2-idees.md)), complexité 🟡 moyenne.

Les développements sont répartis sur les tâches T-09.1 à T-09.5 :

| Tâche | Responsable | Périmètre |
|-------|-------------|-----------|
| T-09.1 | Axel | `POST /api/quizzes/generate/` — paramètres `difficulty` + `nb_questions` |
| T-09.2 | Médy | Moteur prompt `quiz_prompt.py` — 3 niveaux + nb variable (intégré à T-09.1) |
| T-09.3 | Amine | UI difficulté + slider 5-20 sur la page de génération |
| T-09.4 | Ryma | Tests pytest génération (bornes + niveaux) |
| T-09.5 | Médy | **Ce document** — note des critères d'acceptation |

---

## 2. Critères d'acceptation (GWT)

### CA-09.1 — Respect du niveau de difficulté

| Rôle | Phrase |
|------|--------|
| **Given** | un cours uploadé et l'utilisateur sur la page de génération |
| **When** | il choisit une difficulté parmi « facile », « moyen » ou « difficile » et soumet |
| **Then** | le quiz généré correspond au niveau demandé |

**Vérification par niveau :**

| Niveau | Comportement attendu |
|--------|----------------------|
| `easy` | Questions directes sur les faits, définitions et exemples explicitement présents dans le cours |
| `medium` (défaut) | Questions de compréhension standard, formulation claire sans piège gratuit |
| `hard` | Questions approfondies, pièges raisonnés et synthèse entre plusieurs passages du cours |

---

### CA-09.2 — Respect du nombre de questions

| Rôle | Phrase |
|------|--------|
| **Given** | un cours uploadé et l'utilisateur sur la page de génération |
| **When** | il choisit un nombre de questions entre 5 et 20 puis soumet |
| **Then** | le quiz généré contient exactement ce nombre de questions |

**Bornes :** 5 ≤ `nb_questions` ≤ 20. Valeur par défaut : 10 (rétrocompatible).

---

### CA-09.3 — Validation des entrées hors limites

| Rôle | Phrase |
|------|--------|
| **Given** | l'utilisateur est sur la page de génération |
| **When** | il soumet `nb_questions < 5` ou `nb_questions > 20`, ou `difficulty` avec une valeur invalide |
| **Then** | la requête est rejetée avec HTTP 400 et un message d'erreur explicite |

---

### CA-09.4 — Latence de génération

| Rôle | Phrase |
|------|--------|
| **Given** | une demande de génération valide est soumise |
| **When** | le backend exécute la génération LLM |
| **Then** | la réponse HTTP 201 est renvoyée en moins de 90 secondes |

Note : ce critère est dépendant des performances du modèle LLM sous-jacent
(local vs cloud). En cas de timeout, un message d'erreur est affiché.

---

## 3. Mappage technique

| Élément | Valeur | Fichier |
|---------|--------|---------|
| Endpoint | `POST /api/quizzes/generate/` | `backend/quizzes/views.py` |
| Paramètre `difficulty` | `easy` / `medium` / `hard` | `backend/quizzes/serializers.py` |
| Valeurs acceptées `nb_questions` | 5 – 20 (défaut 10) | `backend/quizzes/serializers.py` |
| Instructions prompt par niveau | `_DIFFICULTY_INSTRUCTIONS` | `backend/llm/services/quiz_prompt.py` |
| Validation post-génération | `parse_and_validate_quiz(nb_questions)` | `backend/llm/services/quiz_prompt.py` |
| Tests automatisés | Tests paramétrés pytest | `backend/quizzes/tests.py` |
| UI frontend | Slider + sélecteur niveau | `frontend/src/pages/GenerateQuizPage.tsx` |

---

## 4. Définition of Done

- [ ] **CA-09.1** : la génération respecte le niveau `easy` / `medium` / `hard`
- [ ] **CA-09.2** : le nombre de questions générées correspond exactement au paramètre (5-20)
- [ ] **CA-09.3** : les valeurs hors limites sont rejetées proprement (HTTP 400)
- [ ] **CA-09.4** : la latence de génération est mesurée et < 90 s
- [ ] Tests automatisés couvrant les 3 premiers critères
- [ ] Démo fonctionnelle validée en Sprint Review

---

## 5. Références

- [Document d'idées MVP2 — §4 Niveaux de difficulté](08-mvp2-idees.md)
- [ADR Défense prompt injection](adr/003-prompt-injection-defense.md) (partage la couche validation de `quiz_prompt.py`)
- [Backend quiz_prompt.py](../../../backend/llm/services/quiz_prompt.py)
- [Backend tests quiz](../../../backend/quizzes/tests.py)
