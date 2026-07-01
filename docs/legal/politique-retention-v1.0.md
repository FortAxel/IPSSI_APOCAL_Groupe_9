# Politique de rétention des données — EduTutor IA

**Version :** 1.0 — 1er juillet 2026
**Référent :** Délégué à la Protection des Données (DPO) — [à compléter]

---

## 1. Données collectées et durées de conservation

| Catégorie | Données concernées | Durée de conservation | Base légale |
|-----------|-------------------|----------------------|-------------|
| **Compte utilisateur** | Email, nom, prénom, mot de passe (hashé), date d'inscription | Jusqu'à suppression du compte par l'utilisateur ou 2 ans après la dernière connexion (compte inactif) | Consentement (inscription) + Obligation légale (preuve du contrat) |
| **Profil** | Statut de vérification email, date de création | Identique au compte utilisateur (lié par clé étrangère) | Intérêt légitime (sécurité du compte) |
| **Quiz** | Titre, texte source du cours, score, date de création | Jusqu'à suppression du compte (CASCADE) ou 5 ans si le compte reste actif | Exécution du service (le quiz est le cœur du produit) |
| **Questions** | Énoncés, options, bonne réponse, réponse sélectionnée par l'utilisateur | Identique au quiz parent (CASCADE) | Exécution du service |
| **Demandes RGPD (SAR)** | Type de demande, statut, date, notes de traitement | 5 ans après la clôture de la demande (obligation de preuve de conformité) | Obligation légale (Art. 5.2 — responsabilité) |
| **Tokens d'authentification** | Token DRF, session | Supprimés à la déconnexion ou après expiration (24h) | Intérêt légitime (sécurité) |
| **Emails transactionnels** | Logs d'envoi Brevo (vérification email, reset mdp) | 90 jours (rétention côté fournisseur Brevo) | Obligation légale |

### Suppression en cascade

Lorsqu'un utilisateur supprime son compte (`DELETE /api/accounts/profile/`) :
- Le compte `User` est supprimé → suppression en cascade de son `Profile`, de tous ses `Quiz` et `Questions`.
- Les `DataRequest` associés sont conservés (obligation légale de traçabilité).
- Les tokens d'authentification sont révoqués immédiatement.
- La suppression est **définitive** (hard delete). Aucune restauration possible.

---

## 2. Droits des utilisateurs (RGPD)

Conformément au Règlement Général sur la Protection des Données (UE 2016/679), chaque utilisateur dispose des droits suivants :

| Droit | Article | Description | Comment l'exercer |
|-------|---------|-------------|-------------------|
| **Droit d'accès** | Art. 15 | Obtenir la confirmation que ses données sont traitées et en recevoir une copie | Envoyer une demande via le formulaire de contact ou l'endpoint `POST /api/accounts/data-request/` |
| **Droit de rectification** | Art. 16 | Corriger des données inexactes ou incomplètes | Modifier son profil directement depuis la page « Mon profil » |
| **Droit à l'effacement** | Art. 17 | Obtenir la suppression de ses données dans les meilleurs délais | Supprimer son compte depuis « Mon profil → Zone de danger » ou faire une demande formelle |
| **Droit à la portabilité** | Art. 20 | Recevoir ses données dans un format structuré et lisible (JSON) | Endpoint `GET /api/accounts/me/export/` ou demande formelle |
| **Droit d'opposition** | Art. 21 | S'opposer au traitement de ses données pour des raisons liées à sa situation particulière | Demande écrite au DPO |
| **Droit à la limitation** | Art. 18 | Geler temporairement le traitement de ses données | Demande écrite au DPO |

---

## 3. Procédure d'exercice des droits

### 3.1 — Comment faire une demande

1. **En autonomie** (recommandé) :
   - **Accès / Portabilité :** Bouton « Exporter mes données » sur la page Profil, ou endpoint `GET /api/accounts/me/export/`.
   - **Rectification :** Formulaire d'édition du profil.
   - **Effacement :** Bouton « Supprimer mon compte » sur la page Profil.

2. **Par demande formelle** :
   - Envoyer un email au DPO à l'adresse : `dpo@edututor-ia.fr`
   - Utiliser le formulaire de demande disponible dans l'application (`POST /api/accounts/data-request/`)
   - Préciser : identité, droit exercé, coordonnées de réponse

### 3.2 — Délais de réponse

| Phase | Délai |
|-------|-------|
| Accusé de réception | 48 heures ouvrées |
| Traitement de la demande | **1 mois** à compter de la réception (prolongeable de 2 mois en cas de demande complexe — l'utilisateur en est informé) |
| Envoi des données (portabilité) | Immédiat après traitement (lien de téléchargement valable 7 jours) |
| Confirmation d'effacement | 48 heures après suppression effective |

### 3.3 — Vérification d'identité

Pour toute demande formelle, une vérification d'identité peut être exigée :
- Si la demande est faite depuis l'application en étant connecté → identité vérifiée automatiquement (session + token)
- Si la demande est faite par email → une confirmation par retour de mail ou pièce d'identité peut être demandée

### 3.4 — Refus et recours

Un refus de demande doit être **motivé** (par exemple : demande manifestement infondée ou excessive — Art. 12.5). L'utilisateur est informé :
- Des motifs du refus
- De son droit d'introduire une réclamation auprès de la **CNIL** (www.cnil.fr)
- De son droit de former un recours juridictionnel

---

## Hébergement et localisation des données

| Composant | Localisation | Fournisseur |
|-----------|-------------|-------------|
| Base de données (PostgreSQL) | VPS OVH — France | OVHcloud (RGPD conforme) |
| LLM (Ollama) | Machine locale de l'utilisateur | Aucun transfert externe |
| Emails transactionnels | Serveurs Brevo — France | Brevo (ex-Sendinblue) |
| Backups | VPS OVH — France | Chiffrées, rétention 30 jours |

Aucune donnée personnelle n'est transférée hors de l'Union Européenne.

---

## Contact

- **DPO :** [Nom du DPO] — `dpo@edututor-ia.fr`
- **Autorité de contrôle :** CNIL — 3 Place de Fontenoy, 75007 Paris — www.cnil.fr
