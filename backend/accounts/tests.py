"""Tests pédagogiques pour l'app accounts.

Ces tests servent d'exemples : signup, login, logout, accès protégé.
Lancez : pytest accounts/
"""

from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
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
