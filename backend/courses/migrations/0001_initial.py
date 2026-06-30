"""Migration initiale pour le modèle Course."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(help_text="Titre du cours.", max_length=200)),
                (
                    "content",
                    models.TextField(
                        help_text="Contenu textuel du cours (saisie directe ou extrait PDF).",
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Origine du contenu : nom de fichier PDF, URL ou vide si saisie manuelle.",
                        max_length=500,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        help_text="Propriétaire du cours.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="courses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Cours",
                "verbose_name_plural": "Cours",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="course",
            index=models.Index(fields=["user", "-created_at"], name="courses_cou_user_id_7f0e0d_idx"),
        ),
    ]
