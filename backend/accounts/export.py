"""Export RGPD Art. 15 — données personnelles de l'utilisateur authentifié."""

from django.contrib.auth.models import User
from django.utils import timezone

from courses.models import Course
from quizzes.models import Quiz

from .models import get_or_create_profile
from .serializers import UserSerializer


def build_user_data_export(user: User) -> dict:
    """Construit l'export JSON strictement limité à ``user`` (Art. 15 RGPD)."""
    profile = get_or_create_profile(user)
    courses = Course.objects.filter(user=user).order_by("-created_at")
    quizzes = Quiz.objects.filter(user=user).prefetch_related("questions").order_by("-created_at")

    return {
        "exported_at": timezone.now().isoformat(),
        "format_version": "1.0",
        "account": UserSerializer(user).data,
        "profile": {
            "email_verified": profile.email_verified,
            "created_at": profile.created_at.isoformat(),
        },
        "courses": [
            {
                "id": course.id,
                "title": course.title,
                "content": course.content,
                "source": course.source,
                "created_at": course.created_at.isoformat(),
                "updated_at": course.updated_at.isoformat(),
            }
            for course in courses
        ],
        "quizzes": [
            {
                "id": quiz.id,
                "title": quiz.title,
                "source_text": quiz.source_text,
                "score": quiz.score,
                "course_id": quiz.course_id,
                "created_at": quiz.created_at.isoformat(),
                "updated_at": quiz.updated_at.isoformat(),
                "questions": [
                    {
                        "index": question.index,
                        "prompt": question.prompt,
                        "options": question.options,
                        "correct_index": question.correct_index,
                        "selected_index": question.selected_index,
                    }
                    for question in quiz.questions.all()
                ],
            }
            for quiz in quizzes
        ],
        "reports": [],
        "audit_logs": [],
    }
