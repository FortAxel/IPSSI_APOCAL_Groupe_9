"""Tests pour l'app llm — K1 (ping) + K2 (generate-quiz)."""

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient

from llm.pdf_utils import MAX_PDF_SIZE_BYTES, PDFError
from quizzes.models import Quiz

pytestmark = pytest.mark.django_db


@pytest.fixture
def auth_client() -> APIClient:
    user = User.objects.create_user(username="alice", password="motdepasse123")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@override_settings(LLM_BACKEND="mock")
def test_ping_in_mock_mode():
    response = APIClient().get("/api/llm/ping/")
    assert response.status_code == 200
    assert response.data["backend"] == "mock"


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_with_text(auth_client):
    response = auth_client.post(
        "/api/llm/generate-quiz/",
        {
            "title": "Mon cours de test",
            "source_text": "Lorem ipsum " * 50,
        },
        format="multipart",
    )
    assert response.status_code == 201, response.data
    assert response.data["title"] == "Mon cours de test"
    assert len(response.data["questions"]) == 10
    assert Quiz.objects.filter(title="Mon cours de test").count() == 1


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_custom_nb_questions_and_difficulty(auth_client):
    response = auth_client.post(
        "/api/llm/generate-quiz/",
        {
            "title": "Cours custom",
            "source_text": "Lorem ipsum " * 50,
            "nb_questions": 7,
            "difficulty": "hard",
        },
        format="multipart",
    )
    assert response.status_code == 201, response.data
    assert len(response.data["questions"]) == 7


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_with_pdf_upload(auth_client, monkeypatch):
    def fake_extract_text_from_pdf(_pdf_file):
        return "Texte extrait du PDF. " * 20

    monkeypatch.setattr("llm.views.extract_text_from_pdf", fake_extract_text_from_pdf)
    pdf = SimpleUploadedFile(
        "cours.pdf",
        b"%PDF-1.4 fake content",
        content_type="application/pdf",
    )

    response = auth_client.post(
        "/api/llm/generate-quiz/",
        {"title": "Cours PDF", "pdf": pdf},
        format="multipart",
    )

    assert response.status_code == 201, response.data
    assert response.data["title"] == "Cours PDF"
    quiz = Quiz.objects.get(title="Cours PDF")
    assert quiz.source_text.startswith("Texte extrait du PDF.")


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_rejects_non_pdf_upload(auth_client):
    text_file = SimpleUploadedFile(
        "cours.txt",
        b"not a pdf",
        content_type="text/plain",
    )

    response = auth_client.post(
        "/api/llm/generate-quiz/",
        {"title": "Mauvais fichier", "pdf": text_file},
        format="multipart",
    )

    assert response.status_code == 400


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_rejects_pdf_over_5_mb(auth_client, monkeypatch):
    def fake_extract_text_from_pdf(pdf_file):
        if pdf_file.size > MAX_PDF_SIZE_BYTES:
            raise PDFError("PDF trop volumineux (> 5 Mo).")
        return "Texte extrait du PDF. " * 20

    monkeypatch.setattr("llm.views.extract_text_from_pdf", fake_extract_text_from_pdf)
    pdf = SimpleUploadedFile(
        "gros-cours.pdf",
        b"x" * (MAX_PDF_SIZE_BYTES + 1),
        content_type="application/pdf",
    )

    response = auth_client.post(
        "/api/llm/generate-quiz/",
        {"title": "PDF trop gros", "pdf": pdf},
        format="multipart",
    )

    assert response.status_code == 400
    assert "PDF trop volumineux" in response.data["detail"]


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_requires_text_or_pdf(auth_client):
    response = auth_client.post(
        "/api/llm/generate-quiz/",
        {"title": "Sans contenu"},
        format="multipart",
    )
    assert response.status_code == 400


@override_settings(LLM_BACKEND="mock")
def test_generate_quiz_rejects_short_text(auth_client):
    response = auth_client.post(
        "/api/llm/generate-quiz/",
        {"title": "Trop court", "source_text": "Court"},
        format="multipart",
    )
    assert response.status_code == 400


def test_generate_quiz_requires_auth():
    response = APIClient().post(
        "/api/llm/generate-quiz/",
        {"title": "X", "source_text": "x" * 200},
        format="multipart",
    )
    assert response.status_code in (401, 403)
