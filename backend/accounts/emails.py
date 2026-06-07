"""
Helpers d'envoi d'email pour l'app accounts.

[Note pédagogique] On centralise ici l'envoi d'email. Le backend réel (SMTP
Brevo ou console) est choisi automatiquement dans settings.py selon la présence
d'une clé Brevo. Le code applicatif n'a donc PAS à savoir COMMENT l'email part :
il appelle simplement send_email(). C'est une bonne séparation des
responsabilités (le « quoi » envoyer vs le « comment » l'envoyer).

Au Lot 3, ce module accueillera les emails métier : validation de compte et
réinitialisation de mot de passe (avec leurs liens et leurs tokens).
"""
from smtplib import SMTPAuthenticationError, SMTPException

from django.conf import settings
from django.core.mail import send_mail


class EmailError(Exception):
    """Erreur d'envoi d'email, avec un message déjà explicite pour l'utilisateur."""


def send_email(to_email: str, subject: str, body: str) -> None:
    """Envoie un email texte simple.

    En mode console (dev, pas de clé Brevo), l'email est écrit dans les logs.
    Avec une clé Brevo, un vrai email part via SMTP.

    Raises:
        EmailError: avec un message clair si l'envoi échoue (clé expirée, etc.).
    """
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
    except SMTPAuthenticationError as exc:
        # 535 = identifiants refusés. En formation, la clé Brevo est TEMPORAIRE :
        # ce cas se produira typiquement quand elle aura expiré.
        raise EmailError(
            "Authentification Brevo refusée (clé SMTP expirée ou invalide). "
            "En formation, la clé est temporaire : demandez la clé à jour à votre "
            "formateur, ou laissez BREVO_SMTP_KEY vide dans le .env pour repasser "
            "en mode console (emails affichés dans les logs)."
        ) from exc
    except SMTPException as exc:
        # Autres erreurs SMTP (expéditeur non validé, quota dépassé, réseau…).
        raise EmailError(f"Échec de l'envoi de l'email via SMTP : {exc}") from exc
