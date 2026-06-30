"""Tests pour l'app quizzes — K1 (list/detail) + K2 (answer) + T-03.3 (generate)."""

import time
import pytest
from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APIClient

from courses.models import Course

from .models import Question, Quiz

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> User:
    return User.objects.create_user(username="alice", password="motdepasse123")


@pytest.fixture
def other_user() -> User:
    return User.objects.create_user(username="bob", password="motdepasse123")


@pytest.fixture
def auth_client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def sample_quiz(user) -> Quiz:
    quiz = Quiz.objects.create(
        user=user,
        title="Cours de test",
        source_text="Lorem ipsum dolor sit amet.",
        score=None,
    )
    for i in range(1, 11):
        Question.objects.create(
            quiz=quiz,
            index=i,
            prompt=f"Question {i} ?",
            options=["A", "B", "C", "D"],
            correct_index=0,  # bonne réponse = A pour toutes
        )
    return quiz


def test_quiz_list_requires_auth():
    response = APIClient().get("/api/quizzes/")
    assert response.status_code in (401, 403)


def test_quiz_list_returns_user_quizzes(auth_client, sample_quiz):
    response = auth_client.get("/api/quizzes/")
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["nb_questions"] == 10


def test_quiz_list_does_not_leak_other_users_quizzes(auth_client, other_user):
    Quiz.objects.create(user=other_user, title="Quiz de Bob", source_text="...")
    response = auth_client.get("/api/quizzes/")
    assert response.data["count"] == 0


def test_quiz_detail(auth_client, sample_quiz):
    response = auth_client.get(f"/api/quizzes/{sample_quiz.id}/")
    assert response.status_code == 200
    assert len(response.data["questions"]) == 10


def test_quiz_detail_404_for_other_users_quiz(auth_client, other_user):
    other_quiz = Quiz.objects.create(user=other_user, title="Privé", source_text="...")
    response = auth_client.get(f"/api/quizzes/{other_quiz.id}/")
    assert response.status_code == 404


# --- T-03.3 : generate endpoint ---


@pytest.fixture
def sample_course(user) -> Course:
    return Course.objects.create(
        user=user,
        title="Droit civil",
        content="Article 1101 du code civil. " * 20,
    )


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_from_course(auth_client, sample_course):
    response = auth_client.post(
        "/api/quizzes/generate/",
        {"course_id": sample_course.id},
        format="json",
    )
    assert response.status_code == 201, response.data
    assert response.data["title"] == "Droit civil"
    assert len(response.data["questions"]) == 10
    assert Quiz.objects.filter(title="Droit civil").count() == 1


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_performance_under_60_seconds(auth_client, sample_course):
    start = time.perf_counter()
    response = auth_client.post(
        "/api/quizzes/generate/",
        {"course_id": sample_course.id},
        format="json",
    )
    elapsed = time.perf_counter() - start
    assert response.status_code == 201, response.data
    assert elapsed < 60, f"Generation took trop longtemps : {elapsed:.2f}s"


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_rejects_short_course(auth_client, user):
    course = Course.objects.create(
        user=user,
        title="Trop court",
        content="Court",
    )
    response = auth_client.post(
        "/api/quizzes/generate/",
        {"course_id": course.id},
        format="json",
    )
    assert response.status_code == 400


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_404_for_other_users_course(auth_client, other_user):
    course = Course.objects.create(
        user=other_user,
        title="Privé",
        content="Lorem ipsum dolor sit amet. " * 20,
    )
    response = auth_client.post(
        "/api/quizzes/generate/",
        {"course_id": course.id},
        format="json",
    )
    assert response.status_code == 404


def test_generate_quiz_requires_auth():
    response = APIClient().post(
        "/api/quizzes/generate/",
        {"course_id": 1},
        format="json",
    )
    assert response.status_code in (401, 403)


# --- T-04.2 : answer endpoint ---


def test_answer_all_correct(auth_client, sample_quiz):
    """Toutes les bonnes réponses (= 0 partout) → score 10/10."""
    response = auth_client.post(
        f"/api/quizzes/{sample_quiz.id}/answer/",
        {"answers": [{"index": i, "selected_index": 0} for i in range(1, 11)]},
        format="json",
    )
    assert response.status_code == 200, response.data
    assert response.data["score"] == 10
    assert response.data["total"] == 10
    assert all(d["correct"] for d in response.data["details"])
    sample_quiz.refresh_from_db()
    assert sample_quiz.score == 10
    for q in sample_quiz.questions.all():
        assert q.selected_index == 0


def test_answer_persists_wrong_selected_index(auth_client, sample_quiz):
    """US-04 : chaque réponse incorrecte est enregistrée avec son statut."""
    response = auth_client.post(
        f"/api/quizzes/{sample_quiz.id}/answer/",
        {"answers": [{"index": 1, "selected_index": 2}] + [
            {"index": i, "selected_index": 0} for i in range(2, 11)
        ]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["details"][0]["correct"] is False
    q1 = sample_quiz.questions.get(index=1)
    q1.refresh_from_db()
    assert q1.selected_index == 2


def test_answer_all_wrong(auth_client, sample_quiz):
    response = auth_client.post(
        f"/api/quizzes/{sample_quiz.id}/answer/",
        {"answers": [{"index": i, "selected_index": 1} for i in range(1, 11)]},
        format="json",
    )
    assert response.data["score"] == 0


def test_answer_partial(auth_client, sample_quiz):
    """5 bonnes + 5 mauvaises."""
    answers = [{"index": i, "selected_index": 0} for i in range(1, 6)] + [
        {"index": i, "selected_index": 1} for i in range(6, 11)
    ]
    response = auth_client.post(
        f"/api/quizzes/{sample_quiz.id}/answer/",
        {"answers": answers},
        format="json",
    )
    assert response.data["score"] == 5


def test_answer_requires_10(auth_client, sample_quiz):
    response = auth_client.post(
        f"/api/quizzes/{sample_quiz.id}/answer/",
        {"answers": [{"index": 1, "selected_index": 0}]},
        format="json",
    )
    assert response.status_code == 400


def test_answer_rejects_duplicate_index(auth_client, sample_quiz):
    response = auth_client.post(
        f"/api/quizzes/{sample_quiz.id}/answer/",
        {
            "answers": [{"index": 1, "selected_index": 0}] * 10,
        },
        format="json",
    )
    assert response.status_code == 400


def test_answer_404_for_other_users_quiz(auth_client, other_user):
    other_quiz = Quiz.objects.create(user=other_user, title="Privé", source_text="...")
    for i in range(1, 11):
        Question.objects.create(
            quiz=other_quiz,
            index=i,
            prompt=f"Q{i}",
            options=["A", "B", "C", "D"],
            correct_index=0,
        )
    response = auth_client.post(
        f"/api/quizzes/{other_quiz.id}/answer/",
        {"answers": [{"index": i, "selected_index": 0} for i in range(1, 11)]},
        format="json",
    )
    assert response.status_code == 404
