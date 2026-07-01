"""Tests pédagogiques pour l'app accounts.

Ces tests servent d'exemples : signup, login, logout, accès protégé.
Lancez : pytest accounts/
"""

import io
import zipfile as _zipfile
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.tokens import make_password_reset_tokens

pytestmark = pytest.mark.django_db


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        username="alice", email="alice@test.com", password="motdepasse123"
    )


def test_signup_creates_user(client):
    response = client.post(
        "/api/accounts/signup/",
        {
            "email": "bob@test.com",
            "password": "motdepasse123",
        },
        format="json",
    )
    assert response.status_code == 201, response.data
    assert User.objects.filter(email="bob@test.com").exists()


def test_signup_normalizes_email_and_uses_it_as_username(client):
    response = client.post(
        "/api/accounts/signup/",
        {
            "email": "  BOB@TEST.COM  ",
            "password": "motdepasse123",
            "first_name": "Bob",
        },
        format="json",
    )

    assert response.status_code == 201, response.data
    user = User.objects.get(email="bob@test.com")
    assert user.username == "bob@test.com"
    assert user.first_name == "Bob"


def test_signup_requires_email(client):
    response = client.post(
        "/api/accounts/signup/",
        {"password": "motdepasse123"},
        format="json",
    )
    assert response.status_code == 400


def test_signup_rejects_short_password(client):
    response = client.post(
        "/api/accounts/signup/",
        {"email": "short@test.com", "password": "1234567"},
        format="json",
    )
    assert response.status_code == 400
    assert not User.objects.filter(email="short@test.com").exists()


def test_signup_rejects_duplicate_email_case_insensitive(client, user):
    response = client.post(
        "/api/accounts/signup/",
        {"email": "ALICE@TEST.COM", "password": "motdepasse123"},
        format="json",
    )
    assert response.status_code == 400
    assert User.objects.filter(email__iexact="alice@test.com").count() == 1


def test_login_returns_token(client, user):
    response = client.post(
        "/api/accounts/login/",
        {"email": "alice@test.com", "password": "motdepasse123"},
        format="json",
    )
    assert response.status_code == 200, response.data
    assert "token" in response.data
    assert response.data["user"]["email"] == "alice@test.com"


def test_login_with_wrong_password(client, user):
    response = client.post(
        "/api/accounts/login/",
        {"email": "alice@test.com", "password": "wrong"},
        format="json",
    )
    assert response.status_code == 400


def test_password_reset_request_returns_success(client, user):
    with patch("accounts.views.send_password_reset_email") as mock_send:
        response = client.post(
            "/api/accounts/password-reset/",
            {"email": "alice@test.com"},
            format="json",
        )
    assert response.status_code == 200
    mock_send.assert_called_once_with(user)


def test_password_reset_confirm_changes_password(client, user):
    uidb64, token = make_password_reset_tokens(user)
    response = client.post(
        "/api/accounts/password-reset/confirm/",
        {"uid": uidb64, "token": token, "new_password": "nouveauMotDePasse123"},
        format="json",
    )
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("nouveauMotDePasse123")


def test_me_requires_auth(client):
    response = client.get("/api/accounts/me/")
    assert response.status_code in (401, 403)


def test_me_with_token(client, user):
    from rest_framework.authtoken.models import Token

    token = Token.objects.create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    response = client.get("/api/accounts/me/")
    assert response.status_code == 200
    assert response.data["username"] == "alice"


def test_logout_invalidates_token(client, user):
    from rest_framework.authtoken.models import Token

    token = Token.objects.create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    response = client.post("/api/accounts/logout/")
    assert response.status_code == 204
    assert not Token.objects.filter(key=token.key).exists()


# --- T-07.1 (US-07) : réinitialisation de mot de passe ---


RESET_DETAIL = (
    "Si un compte existe pour cet email, un lien de réinitialisation vient d'être envoyé."
)


def test_password_reset_request_same_response_unknown_email(client):
    """Anti-énumération : même réponse que l'email existe ou non."""
    response = client.post(
        "/api/accounts/password-reset/",
        {"email": "inconnu@test.com"},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["detail"] == RESET_DETAIL


def test_password_reset_request_same_response_known_email(client, user):
    from unittest.mock import patch

    with patch("accounts.views.send_password_reset_email"):
        response = client.post(
            "/api/accounts/password-reset/",
            {"email": "alice@test.com"},
            format="json",
        )
    assert response.status_code == 200
    assert response.data["detail"] == RESET_DETAIL


def test_password_reset_request_sends_email_for_known_user(client, user):
    from unittest.mock import patch

    with patch("accounts.views.send_password_reset_email") as mock_send:
        client.post(
            "/api/accounts/password-reset/",
            {"email": "alice@test.com"},
            format="json",
        )
    mock_send.assert_called_once_with(user)


def test_password_reset_request_does_not_send_for_unknown_email(client):
    from unittest.mock import patch

    with patch("accounts.views.send_password_reset_email") as mock_send:
        client.post(
            "/api/accounts/password-reset/",
            {"email": "inconnu@test.com"},
            format="json",
        )
    mock_send.assert_not_called()


def test_password_reset_confirm_sets_new_password(client, user):
    from accounts.tokens import make_password_reset_tokens

    uid, token = make_password_reset_tokens(user)
    response = client.post(
        "/api/accounts/password-reset/confirm/",
        {"uid": uid, "token": token, "new_password": "nouveauMotDePasse1"},
        format="json",
    )
    assert response.status_code == 200, response.data
    user.refresh_from_db()
    assert user.check_password("nouveauMotDePasse1")


def test_password_reset_confirm_allows_login_with_new_password(client, user):
    from accounts.tokens import make_password_reset_tokens

    uid, token = make_password_reset_tokens(user)
    client.post(
        "/api/accounts/password-reset/confirm/",
        {"uid": uid, "token": token, "new_password": "nouveauMotDePasse1"},
        format="json",
    )
    response = client.post(
        "/api/accounts/login/",
        {"email": "alice@test.com", "password": "nouveauMotDePasse1"},
        format="json",
    )
    assert response.status_code == 200, response.data
    assert "token" in response.data


def test_password_reset_confirm_rejects_invalid_token(client, user):
    from accounts.tokens import make_password_reset_tokens

    uid, _ = make_password_reset_tokens(user)
    response = client.post(
        "/api/accounts/password-reset/confirm/",
        {"uid": uid, "token": "token-invalide", "new_password": "nouveauMotDePasse1"},
        format="json",
    )
    assert response.status_code == 400
    assert "invalide" in response.data["detail"].lower()


def test_password_reset_confirm_rejects_expired_token(client, user):
    from datetime import datetime, timedelta
    from unittest.mock import patch

    from accounts.tokens import make_password_reset_tokens, password_reset_token_generator

    uid, token = make_password_reset_tokens(user)
    expired_now = datetime.now() + timedelta(hours=25)
    with patch.object(password_reset_token_generator, "_now", return_value=expired_now):
        response = client.post(
            "/api/accounts/password-reset/confirm/",
            {"uid": uid, "token": token, "new_password": "nouveauMotDePasse1"},
            format="json",
        )
    assert response.status_code == 400


def test_password_reset_confirm_rejects_short_password(client, user):
    from accounts.tokens import make_password_reset_tokens

    uid, token = make_password_reset_tokens(user)
    response = client.post(
        "/api/accounts/password-reset/confirm/",
        {"uid": uid, "token": token, "new_password": "court"},
        format="json",
    )
    assert response.status_code == 400
    user.refresh_from_db()
    assert user.check_password("motdepasse123")


def test_password_reset_token_max_age_is_24_hours():
    from accounts.tokens import PASSWORD_RESET_MAX_AGE

    assert PASSWORD_RESET_MAX_AGE == 60 * 60 * 24


# --- T-12.2 : export ZIP ---


@pytest.fixture
def auth_client_export(user) -> APIClient:
    c = APIClient()
    token = Token.objects.create(user=user)
    c.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return c


def test_export_json_format_unchanged(auth_client_export):
    """T-12.2 — le format JSON par défaut (sans ?format=) reste inchangé."""
    response = auth_client_export.get("/api/accounts/me/export/")
    assert response.status_code == 200
    assert ".json" in response["Content-Disposition"]


def test_export_zip_status_and_content_type(auth_client_export):
    """T-12.2 — ?export_format=zip renvoie 200 + application/zip."""
    response = auth_client_export.get("/api/accounts/me/export/?export_format=zip")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/zip"


def test_export_zip_content_disposition(auth_client_export):
    """T-12.2 — Content-Disposition : attachment avec un nom de fichier .zip."""
    response = auth_client_export.get("/api/accounts/me/export/?export_format=zip")
    cd = response["Content-Disposition"]
    assert "attachment" in cd
    assert ".zip" in cd


def test_export_zip_contains_three_files(auth_client_export):
    """T-12.2 — L'archive contient quizzes.json, responses.csv et audit.json."""
    response = auth_client_export.get("/api/accounts/me/export/?export_format=zip")
    with _zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        names = zf.namelist()
    assert "quizzes.json" in names
    assert "responses.csv" in names
    assert "audit.json" in names


def test_export_zip_responses_csv_includes_quiz_data(auth_client_export, user):
    """T-12.2 — responses.csv contient les lignes des questions répondues."""
    from courses.models import Course
    from quizzes.models import Question, Quiz

    course = Course.objects.create(user=user, title="Cours test", content="Lorem ipsum " * 20)
    quiz = Quiz.objects.create(user=user, title="Quiz test", source_text="...", course=course)
    Question.objects.create(
        quiz=quiz,
        index=1,
        prompt="Quelle est la couleur du ciel ?",
        options=["Rouge", "Vert", "Bleu", "Jaune"],
        correct_index=2,
        selected_index=1,
    )

    response = auth_client_export.get("/api/accounts/me/export/?export_format=zip")
    with _zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        csv_content = zf.read("responses.csv").decode()

    assert "quiz_id" in csv_content
    assert "is_correct" in csv_content
    assert "Quelle est la couleur du ciel ?" in csv_content


def test_export_zip_requires_auth():
    """T-12.2 — export ZIP inaccessible sans authentification."""
    response = APIClient().get("/api/accounts/me/export/?export_format=zip")
    assert response.status_code in (401, 403)
