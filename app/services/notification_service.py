"""
Application/use-case layer: NotificationService only depends on
IEmailVerifier and IEmailSender — never on AbstractAPI or Resend
directly. Swapping either provider is a one-line change in
container.py and never touches this file (same Dependency Inversion
pattern as AuthService).

The whole "dummy vs real email" feature lives in exactly one place: the
guard at the top of notify_signup / notify_login. A dummy/test address
(sam@gmail.com, asdf@asdf.com, ...) fails IEmailVerifier.is_real() and
the method quietly no-ops — no email goes out, no error is raised,
register/login are completely unaffected either way.
"""
import logging

from app.core.interfaces.email_sender import IEmailSender
from app.core.interfaces.email_verifier import IEmailVerifier
from app.infrastructure.email.templates import login_alert_email_html, welcome_email_html

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(
        self,
        email_verifier: IEmailVerifier,
        email_sender: IEmailSender,
        app_name: str,
        app_logo_url: str | None,
        frontend_url: str,
    ):
        self._verifier = email_verifier
        self._sender = email_sender
        self._app_name = app_name
        self._logo_url = app_logo_url
        self._frontend_url = frontend_url

    def notify_signup(self, name: str, email: str) -> None:
        """Fire-and-forget welcome email, sent once right after a
        successful register — only if `email` verifies as real."""
        if not self._verifier.is_real(email):
            logger.info("Signup welcome email skipped for '%s' — looks like a dummy/test address", email)
            return

        html = welcome_email_html(
            customer_name=name or "there",
            shop_name=self._app_name,
            logo_url=self._logo_url,
            cta_url=self._frontend_url,
        )
        self._sender.send(
            to_email=email,
            to_name=name,
            subject=f"Welcome to {self._app_name}! \U0001F389",
            html_body=html,
        )

    def notify_login(self, name: str, email: str, device_info: str = "a device we don't recognize") -> None:
        """Fire-and-forget security alert, sent on every successful
        login — only if `email` verifies as real."""
        if not self._verifier.is_real(email):
            logger.info("Login alert email skipped for '%s' — looks like a dummy/test address", email)
            return

        html = login_alert_email_html(
            customer_name=name or "there",
            app_name=self._app_name,
            logo_url=self._logo_url,
            device_info=device_info,
            cta_url=f"{self._frontend_url}/account/security",
        )
        self._sender.send(
            to_email=email,
            to_name=name,
            subject="New sign-in to your account",
            html_body=html,
        )
