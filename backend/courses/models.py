"""Modèle Course — support de cours déposé par l'utilisateur (F2)."""

from django.conf import settings
from django.db import models


class Course(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        help_text="Propriétaire du cours.",
    )
    title = models.CharField(max_length=200, help_text="Titre du cours.")
    source_text = models.TextField(
        help_text="Texte source extrait du PDF ou saisi par l'utilisateur.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.user.username}"
