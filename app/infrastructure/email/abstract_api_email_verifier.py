"""
Adapter around AbstractAPI's Email Validation & Verification endpoint.

Docs:   https://www.abstractapi.com/api/email-verification-validation-api
Get a free API key at: https://app.abstractapi.com/api/email-verification/

This is the ONE file in the app that knows AbstractAPI exists. Swapping to
ZeroBounce, Hunter.io, or a hosted SMTP-handshake checker means writing a
new class here that implements IEmailVerifier and changing one line in
container.py — nothing else in the app changes.
"""
from __future__ import annotations

import logging

import httpx

from app.core.interfaces.email_verifier import IEmailVerifier

logger = logging.getLogger(__name__)

_ENDPOINT = "https://emailvalidation.abstractapi.com/v1/"

# Deliverability values AbstractAPI returns that we treat as "real enough
# to email". "UNKNOWN" happens for providers that block verification
# probes (some corporate mail servers) — we don't want to silently punish
# real users there, so it's allowed through by default.
_ACCEPTED_DELIVERABILITY = {"DELIVERABLE", "UNKNOWN"}


class AbstractApiEmailVerifier(IEmailVerifier):
    def __init__(self, api_key: str | None, timeout_seconds: float = 5.0):
        self._api_key = api_key
        self._timeout = timeout_seconds

    def is_real(self, email: str) -> bool:
        if not self._api_key:
            logger.warning(
                "ABSTRACT_API_KEY is not set — skipping email verification, "
                "treating '%s' as real. Set ABSTRACT_API_KEY in .env to enable it.",
                email,
            )
            return True

        try:
            response = httpx.get(
                _ENDPOINT,
                params={"api_key": self._api_key, "email": email},
                timeout=self._timeout,
            )
            response.raise_for_status()
            data = response.json()
        except Exception:
            logger.exception(
                "Email verification API call failed for '%s' — failing open (treating as real)",
                email,
            )
            return True

        is_valid_format = bool(data.get("is_valid_format", {}).get("value", True))
        is_disposable = bool(data.get("is_disposable_email", {}).get("value", False))
        deliverability = data.get("deliverability", "UNKNOWN")

        is_real = is_valid_format and not is_disposable and deliverability in _ACCEPTED_DELIVERABILITY

        logger.info(
            "Email verification for '%s': format_ok=%s disposable=%s deliverability=%s -> real=%s",
            email, is_valid_format, is_disposable, deliverability, is_real,
        )
        return is_real
