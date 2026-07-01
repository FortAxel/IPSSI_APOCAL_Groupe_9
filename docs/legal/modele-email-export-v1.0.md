# Modèle d'email — Réponse à une demande d'export de données (Art. 15 / Art. 20 RGPD)

**Usage :** À envoyer à l'utilisateur après traitement d'une demande `DataRequest` de type `access` ou `portability`.

**Expéditeur :** `dpo@edututor-ia.fr`
**Objet par défaut :** `[EduTutor IA] Vos données personnelles — Demande #{request_id}`

---

**Objet :** Vos données personnelles — Demande d'accès #{request_id}

Bonjour {user.first_name},

Nous donnons suite à votre demande d'exercice de droit d'accès (Art. 15 du RGPD) en date du {request.created_at:dd/mm/yyyy}.

Vos données personnelles sont disponibles en pièce jointe au format JSON structuré. Ce fichier contient :

- Vos informations de compte (email, nom, prénom, date d'inscription)
- L'historique de vos quiz (titres, textes sources, scores, dates)
- Les questions et réponses associées à chaque quiz
- L'historique de vos demandes RGPD antérieures (le cas échéant)

**Le lien de téléchargement est valable 7 jours.** Passé ce délai, le fichier sera supprimé de nos serveurs et vous devrez formuler une nouvelle demande.

---

### Vos droits

Pour rappel, vous disposez également des droits suivants :

- **Rectification (Art. 16) :** modifier vos informations directement depuis votre profil
- **Effacement (Art. 17) :** supprimer définitivement votre compte et toutes vos données
- **Portabilité (Art. 20) :** recevoir vos données dans un format lisible — c'est l'objet de cet email
- **Opposition et limitation (Art. 18, 21) :** nous contacter pour toute demande spécifique

Pour exercer ces droits, connectez-vous à votre espace EduTutor IA ou contactez-nous à cette adresse.

---

### Contact

- **DPO :** {dpo_name} — `dpo@edututor-ia.fr`
- **Demande RGPD n° :** #{request_id} — conservée dans notre registre de traitement pendant 5 ans (obligation légale de traçabilité)
- **Autorité de contrôle :** CNIL — www.cnil.fr

Cordialement,

{dpo_name}
Délégué à la Protection des Données
EduTutor IA
