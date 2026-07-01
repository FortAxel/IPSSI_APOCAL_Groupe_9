"""
Modèles de l'app accounts.

[Note pédagogique] On garde le modèle User standard de Django (simple et
robuste), et on lui ajoute un Profil 1-pour-1 pour les infos métier qui ne sont
pas dans User — ici `email_verified` (l'utilisateur a-t-il cliqué le lien de
confirmation envoyé par email ?).

Choix d'architecture « email = identifiant » : à l'inscription, on met
username = email (voir SignupSerializer). Le login se fait donc par email, sans
backend d'authentification custom. C'est le compromis le plus simple pour un
kit pédagogique (un vrai produit utiliserait souvent un User personnalisé avec
USERNAME_FIELD = 'email').
"""

from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Informations complémentaires attachées à un utilisateur."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    # Validation "soft" : le compte fonctionne même si l'email n'est pas vérifié,
    # mais un bandeau invite l'utilisateur à cliquer le lien de confirmation.
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Profile<{self.user.email or self.user.username}>"


def get_or_create_profile(user) -> Profile:
    """Récupère (ou crée) le profil d'un utilisateur.

    Pratique pour les comptes créés AVANT l'ajout du modèle Profile (ils n'ont
    pas encore de profil) : on le crée à la volée plutôt que de planter.
    """
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


# ---------------------------------------------------------------------------
# RGPD — Modèle d'audit trail pour les demandes d'exercice de droits (SAR)
# ---------------------------------------------------------------------------
# Art. 15 (accès), Art. 17 (effacement), Art. 20 (portabilité), Art. 16 (rectification).
# Chaque demande est tracée avec son statut et un horodatage pour constituer
# une piste d'audit réglementaire. Accessible via l'admin Django pour le DPO.
# ---------------------------------------------------------------------------


class DataRequest(models.Model):
    """Trace l'historique des demandes RGPD d'un utilisateur (audit trail SAR)."""

    class RequestType(models.TextChoices):
        ACCESS = "access", "Droit d'accès (Art. 15)"
        PORTABILITY = "portability", "Portabilité (Art. 20)"
        ERASURE = "erasure", "Effacement (Art. 17)"
        RECTIFICATION = "rectification", "Rectification (Art. 16)"

    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        IN_PROGRESS = "in_progress", "En cours"
        COMPLETED = "completed", "Traité"
        REJECTED = "rejected", "Rejeté"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="data_requests",
    )
    request_type = models.CharField(max_length=20, choices=RequestType.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="handled_requests",
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Demande RGPD"
        verbose_name_plural = "Demandes RGPD"

    def __str__(self) -> str:
        return (
            f"DataRequest #{self.pk} — {self.get_request_type_display()} "
            f"par {self.user.email} [{self.get_status_display()}]"
        )
