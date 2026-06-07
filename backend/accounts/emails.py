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
from django.conf import settings
from django.core.mail import send_mail


def send_email(to_email: str, subject: str, body: str) -> None:
    """Envoie un email texte simple.

    En mode console (dev, pas de clé Brevo), l'email est écrit dans les logs du
    backend. Avec une clé Brevo, un vrai email part via SMTP.

    Raises:
        Exception: si l'envoi échoue avec un backend réel (fail_silently=False
            pour que les erreurs SMTP soient visibles plutôt que silencieuses).
    """
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
    )
