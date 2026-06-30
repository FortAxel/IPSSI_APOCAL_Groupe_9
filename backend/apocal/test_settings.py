"""Configuration locale pour lancer pytest sans Docker/PostgreSQL."""

from .settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test.sqlite3",  # noqa: F405
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
LLM_BACKEND = "mock"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
