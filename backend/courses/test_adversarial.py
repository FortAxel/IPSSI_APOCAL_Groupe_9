"""Adversarial tests for courses-related leakage."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from courses.models import Course

pytestmark = pytest.mark.django_db


@pytest.mark.adversarial
def test_cannot_generate_quiz_from_other_users_course():
    alice = User.objects.create_user(username="alice", password="motdepasse123")
    bob = User.objects.create_user(username="bob", password="motdepasse123")

    course = Course.objects.create(
        user=bob, title="Privé", content="Lorem ipsum dolor sit amet. " * 10
    )

    client = APIClient()
    client.force_authenticate(user=alice)

    response = client.post("/api/quizzes/generate/", {"course_id": course.id}, format="json")
    assert response.status_code == 404
