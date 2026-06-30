"""Ajout de la FK course sur Quiz (T-03.2)."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quizzes", "0002_question_selected_index"),
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="quiz",
            name="course",
            field=models.ForeignKey(
                blank=True,
                help_text="Cours source à partir duquel ce quiz a été généré.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="quizzes",
                to="courses.course",
            ),
        ),
    ]
