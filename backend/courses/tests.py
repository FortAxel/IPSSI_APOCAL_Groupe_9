"""Tests pour POST /api/courses/ — dépôt PDF (T-02.2) et texte (T-02.3)."""

from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from courses.models import Course
from llm.pdf_utils import PDFError

pytestmark = pytest.mark.django_db

SAMPLE_TEXT = "Introduction au droit civil. " * 20


@pytest.fixture
def alice() -> User:
    return User.objects.create_user(username="alice", password="motdepasse123")


@pytest.fixture
def bob() -> User:
    return User.objects.create_user(username="bob", password="motdepasse123")


@pytest.fixture
def alice_client(alice) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=alice)
    return client


@pytest.fixture
def bob_client(bob) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=bob)
    return client


def _pdf_file(name: str = "cours.pdf") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, b"%PDF-1.4 fake content", content_type="application/pdf")


@patch("courses.views.extract_text_from_pdf", return_value=SAMPLE_TEXT)
def test_create_course_from_pdf(mock_extract, auth_client):
    response = auth_client.post(
        "/api/courses/",
        {"title": "Droit civil", "pdf": _pdf_file()},
        format="multipart",
    )
    assert response.status_code == 201, response.data
    assert response.data["title"] == "Droit civil"
    assert response.data["source_text"] == SAMPLE_TEXT
    assert Course.objects.filter(title="Droit civil").count() == 1
    mock_extract.assert_called_once()


@patch(
    "courses.views.extract_text_from_pdf",
    side_effect=PDFError("PDF trop volumineux (> 5 Mo)."),
)
def test_create_course_rejects_oversized_pdf(_mock_extract, auth_client):
    response = auth_client.post(
        "/api/courses/",
        {"title": "Trop gros", "pdf": _pdf_file()},
        format="multipart",
    )
    assert response.status_code == 400
    assert "5 Mo" in response.data["detail"]


def test_create_course_rejects_non_pdf(auth_client):
    fichier = SimpleUploadedFile("notes.txt", b"du texte", content_type="text/plain")
    response = auth_client.post(
        "/api/courses/",
        {"title": "Notes", "pdf": fichier},
        format="multipart",
    )
    assert response.status_code == 400


def test_create_course_requires_text_or_pdf(auth_client):
    response = auth_client.post(
        "/api/courses/",
        {"title": "Sans contenu"},
        format="multipart",
    )
    assert response.status_code == 400


def test_create_course_from_text(auth_client):
    texte = "Lorem ipsum dolor sit amet. " * 10
    response = auth_client.post(
        "/api/courses/",
        {"title": "Cours collé", "source_text": texte},
        format="json",
    )
    assert response.status_code == 201, response.data
    assert response.data["title"] == "Cours collé"
    assert response.data["source_text"] == texte.strip()
    assert Course.objects.filter(title="Cours collé").count() == 1


def test_create_course_rejects_short_text(auth_client):
    response = auth_client.post(
        "/api/courses/",
        {"title": "Trop court", "source_text": "Court"},
        format="json",
    )
    assert response.status_code == 400


def test_create_course_requires_auth():
    response = APIClient().post(
        "/api/courses/",
        {"title": "X", "pdf": _pdf_file()},
        format="multipart",
    )
    assert response.status_code in (401, 403)


@pytest.mark.adversarial
def test_user_cannot_generate_quiz_from_other_users_course(alice, bob, bob_client):
    course = Course.objects.create(
        user=alice,
        title="Privé d'Alice",
        content="Lorem ipsum dolor sit amet. " * 20,
    )

    response = bob_client.post(
        "/api/quizzes/generate/",
        {"course_id": course.id},
        format="json",
    )
    assert response.status_code in (403, 404)
