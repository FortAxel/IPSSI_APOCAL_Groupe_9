"""
Tokens sécurisés pour la validation d'email et la réinitialisation de mot de passe.

[Note pédagogique] Deux mécanismes complémentaires de Django, SANS stocker de
token en base :
- `django.core.signing` : un token signé (inviolable) qui encode l'id de
  l'utilisateur + une date. Utilisé pour la validation d'email.
- `default_token_generator` (PasswordResetTokenGenerator) : le générateur
  STANDARD de Django pour le reset de mot de passe. Le token devient invalide
  dès que le mot de passe change ou après expiration. C'est le mécanisme
  éprouvé qu'utilise l'admin Django — on ne réinvente pas la roue.
"""

from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import signing
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

EMAIL_VERIFY_SALT = "accounts.email-verification"
EMAIL_VERIFY_MAX_AGE = 60 * 60 * 24 * 3  # 3 jours en secondes


# --- Validation d'email (token signé, sans stockage en base) ---


def make_email_verify_token(user) -> str:
    """Crée un token signé contenant l'id de l'utilisateur."""
    return signing.dumps({"uid": user.pk}, salt=EMAIL_VERIFY_SALT)


def read_email_verify_token(token: str) -> int | None:
    """Renvoie l'id utilisateur si le token est valide et non expiré, sinon None."""
    try:
        data = signing.loads(token, salt=EMAIL_VERIFY_SALT, max_age=EMAIL_VERIFY_MAX_AGE)
        return data.get("uid")
    except signing.BadSignature:
        return None


# --- Réinitialisation de mot de passe (mécanisme standard Django) ---

PASSWORD_RESET_MAX_AGE = 60 * 60 * 24  # 24 heures (T-07.1)


class _PasswordResetTokenGenerator(PasswordResetTokenGenerator):
    """Générateur Django avec validité explicite de 24 h (US-07 / T-07.1)."""

    timeout = PASSWORD_RESET_MAX_AGE

    def check_token(self, user, token):
        """Comme Django, mais expiration pilotée par ``self.timeout`` (24 h)."""
        if not (user and token):
            return False
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        from django.utils.http import base36_to_int

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        from django.utils.crypto import constant_time_compare

        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(
                self._make_token_with_timestamp(user, ts, secret),
                token,
            ):
                break
        else:
            return False

        if (self._num_seconds(self._now()) - ts) > self.timeout:
            return False

        return True


password_reset_token_generator = _PasswordResetTokenGenerator()


def make_password_reset_tokens(user) -> tuple[str, str]:
    """Renvoie (uidb64, token) à mettre dans le lien de réinitialisation."""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token_generator.make_token(user)
    return uidb64, token


def read_password_reset_tokens(uidb64: str, token: str):
    """Renvoie l'utilisateur si (uidb64, token) est valide, sinon None."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return None
    if password_reset_token_generator.check_token(user, token):
        return user
    return None
