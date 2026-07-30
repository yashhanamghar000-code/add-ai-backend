"""
Adapter around Resend's transactional email API.

Docs:      https://resend.com/docs/api-reference/emails/send-email
Get a key: https://resend.com (free tier includes a shared
           onboarding@resend.dev sender for testing before you verify
           your own domain)

This is the ONE file that knows Resend exists. Swapping to SendGrid or
Mailgun means writing a new class here that implements IEmailSender and
changing one line in container.py.
"""
from __future__ import annotations

import logging

import httpx

from app.core.interfaces.email_sender import IEmailSender

logger = logging.getLogger(__name__)

_ENDPOINT = "https://api.resend.com/emails"


class ResendEmailSender(IEmailSender):
    def __init__(self, api_key: str | None, from_email: str, from_name: str, timeout_seconds: float = 8.0):
        self._api_key = api_key
        self._from_email = from_email
        self._from_name = from_name
        self._timeout = timeout_seconds

    def send(self, to_email: str, to_name: str, subject: str, html_body: str) -> None:
        if not self._api_key:
            logger.warning(
                "RESEND_API_KEY is not set — skipping send of %r to %s. "
                "Set RESEND_API_KEY in .env to enable real sending.",
                subject, to_email,
            )
            return

        try:
            response = httpx.post(
                _ENDPOINT,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "from": f"{self._from_name} <{self._from_email}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_body,
                },
                timeout=self._timeout,
            )
            print("=" * 60)
            print("Status:", response.status_code)
            print("Response:", response.text)
            print("=" * 60)

            response.raise_for_status()
            logger.info("Sent email %r to %s", subject, to_email)
        except Exception:
            # A notification email failing to send must never break
            # register/login — it's fired from a FastAPI BackgroundTask
            # specifically so a failure here is isolated and just logged.
            logger.exception("Failed to send email %r to %s", subject, to_email)
