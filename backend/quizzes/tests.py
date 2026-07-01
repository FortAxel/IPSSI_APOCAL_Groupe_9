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


# --- T-06.1 : GET /api/quizzes/ paginé + tri date desc ---


def test_quiz_list_summary_fields(auth_client, sample_quiz):
    response = auth_client.get("/api/quizzes/")
    assert response.status_code == 200
    item = response.data["results"][0]
    assert item["title"] == "Cours de test"
    assert item["score"] is None
    assert "created_at" in item
    assert item["nb_questions"] == 10


def test_quiz_list_sorted_by_created_at_desc(auth_client, user):
    Quiz.objects.create(user=user, title="Ancien", source_text="...", score=5)
    time.sleep(0.01)
    Quiz.objects.create(user=user, title="Récent", source_text="...", score=8)
    response = auth_client.get("/api/quizzes/")
    titles = [q["title"] for q in response.data["results"]]
    assert titles.index("Récent") < titles.index("Ancien")


def test_quiz_list_pagination(auth_client, user):
    for i in range(21):
        Quiz.objects.create(user=user, title=f"Quiz {i}", source_text="...")
    response = auth_client.get("/api/quizzes/")
    assert response.status_code == 200
    assert response.data["count"] == 21
    assert len(response.data["results"]) == 20
    assert response.data["next"] is not None
    assert response.data["previous"] is None


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


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_accepts_difficulty_and_question_bounds(auth_client, sample_course):
    response = auth_client.post(
        "/api/quizzes/generate/",
        {"course_id": sample_course.id, "difficulty": "hard", "nb_questions": 7},
        format="json",
    )

    assert response.status_code == 201, response.data
    assert len(response.data["questions"]) == 7


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_rejects_out_of_range_question_count(auth_client, sample_course):
    response = auth_client.post(
        "/api/quizzes/generate/",
        {"course_id": sample_course.id, "nb_questions": 4},
        format="json",
    )

    assert response.status_code == 400
    assert "nb_questions" in response.data["detail"].lower()


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_rejects_unknown_difficulty(auth_client, sample_course):
    response = auth_client.post(
        "/api/quizzes/generate/",
        {"course_id": sample_course.id, "difficulty": "wizard"},
        format="json",
    )

    assert response.status_code == 400
    assert "difficulty" in response.data["detail"].lower()


def test_answer_quiz_is_blocked_for_other_users(auth_client, other_user):
    other_quiz = Quiz.objects.create(user=other_user, title="Privé", source_text="...")
    response = auth_client.post(
        f"/api/quizzes/{other_quiz.id}/answer/",
        {"answers": [{"index": 1, "selected_index": 0}] * 10},
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
        {
            "answers": [{"index": 1, "selected_index": 2}]
            + [{"index": i, "selected_index": 0} for i in range(2, 11)]
        },
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


def test_answer_returns_details_with_score_and_persistence(auth_client, sample_quiz):
    response = auth_client.post(
        f"/api/quizzes/{sample_quiz.id}/answer/",
        {
            "answers": [
                {"index": 1, "selected_index": 2},
                *[{"index": i, "selected_index": 0} for i in range(2, 11)],
            ]
        },
        format="json",
    )
    assert response.status_code == 200, response.data
    assert response.data["score"] == 9
    assert response.data["total"] == 10
    assert len(response.data["details"]) == 10
    assert response.data["details"][0]["correct"] is False
    assert response.data["details"][0]["selected_index"] == 2
    sample_quiz.refresh_from_db()
    assert sample_quiz.score == 9


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


# --- T-05.1 : exposition score + details[] dans la réponse answer ---


def test_answer_exposes_score_and_details_format(auth_client, sample_quiz):
    """T-05.1 — score et details[] sont présents avec tous les champs attendus.

    Contrat pour Amine (T-05.2 page résultat) et Médy (T-05.4 UX) :
      response.score          → int, 0..10
      response.details        → liste de 10 objets
      details[n].question_id  → int (PK Question)
      details[n].index        → int, 1..10
      details[n].selected_index → int, 0..3
      details[n].correct_index  → int, 0..3
      details[n].is_correct     → bool
    """
    answers = [{"index": i, "selected_index": 0} for i in range(1, 11)]
    response = auth_client.post(
        f"/api/quizzes/{sample_quiz.id}/answer/",
        {"answers": answers},
        format="json",
    )
    assert response.status_code == 200
    data = response.data

    # score
    assert "score" in data, "La réponse doit contenir 'score'"
    assert isinstance(data["score"], int), "score doit être un entier"
    assert 0 <= data["score"] <= 10

    # details présent et complet
    assert "details" in data, "La réponse doit contenir 'details'"
    assert len(data["details"]) == 10, "details doit avoir 10 entrées (une par question)"

    required_keys = {"question_id", "index", "selected_index", "correct_index", "is_correct"}
    for detail in data["details"]:
        missing = required_keys - detail.keys()
        assert not missing, f"Champs manquants dans details : {missing}"
        assert isinstance(detail["question_id"], int)
        assert isinstance(detail["is_correct"], bool)
        assert 1 <= detail["index"] <= 10
        assert 0 <= detail["selected_index"] <= 3
        assert 0 <= detail["correct_index"] <= 3


def test_answer_is_correct_reflects_answer(auth_client, sample_quiz):
    """T-05.1 — is_correct est True si et seulement si selected == correct."""
    # correct_index = 0 pour toutes les questions (cf. fixture sample_quiz)
    answers = [{"index": 1, "selected_index": 0}] + [  # bonne
        {"index": i, "selected_index": 1} for i in range(2, 11)
    ]  # mauvaises
    response = auth_client.post(
        f"/api/quizzes/{sample_quiz.id}/answer/",
        {"answers": answers},
        format="json",
    )
    assert response.status_code == 200
    details = {d["index"]: d for d in response.data["details"]}
    assert details[1]["is_correct"] is True
    for i in range(2, 11):
        assert details[i]["is_correct"] is False


def test_answer_question_id_matches_db(auth_client, sample_quiz):
    """T-05.1 — question_id dans details correspond à la PK en base."""
    response = auth_client.post(
        f"/api/quizzes/{sample_quiz.id}/answer/",
        {"answers": [{"index": i, "selected_index": 0} for i in range(1, 11)]},
        format="json",
    )
    assert response.status_code == 200
    db_ids = set(sample_quiz.questions.values_list("id", flat=True))
    response_ids = {d["question_id"] for d in response.data["details"]}
    assert response_ids == db_ids, "Les question_id doivent correspondre aux PKs en base"


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


@pytest.mark.adversarial
def test_adversarial_enumeration_cannot_access_other_users_quiz(user, other_user):
    """Tentative d'énumération/accès par ID → ne doit pas renvoyer d'autre user data."""
    # Quiz appartenant à Bob
    other_quiz = Quiz.objects.create(user=other_user, title="Secret Quiz", source_text="...")
    for i in range(1, 11):
        Question.objects.create(
            quiz=other_quiz,
            index=i,
            prompt=f"Q{i}",
            options=["A", "B", "C", "D"],
            correct_index=0,
        )

    client = APIClient()
    client.force_authenticate(user=user)

    # Accès direct au détail du quiz d'un autre utilisateur
    resp = client.get(f"/api/quizzes/{other_quiz.id}/")
    assert resp.status_code == 404

    # Tentative d'énumération sur des IDs proches
    for candidate in (other_quiz.id - 1, other_quiz.id + 1, other_quiz.id + 2):
        if candidate <= 0:
            continue
        r = client.get(f"/api/quizzes/{candidate}/")
        assert r.status_code in (404, 401, 403)
