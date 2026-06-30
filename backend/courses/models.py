from django.conf import settings
from django.db import models


class Course(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        help_text="Propriétaire du cours.",
    )
    title = models.CharField(
        max_length=200,
        help_text="Titre du cours.",
    )
    content = models.TextField(
        help_text="Contenu textuel du cours (saisie directe ou extrait PDF).",
    )
    source = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Origine du contenu : nom de fichier PDF, URL ou vide si saisie manuelle.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Cours"
        verbose_name_plural = "Cours"

    def __str__(self) -> str:
        return f"{self.title} — {self.user.username}"
