from abc import ABC, abstractmethod


class IEmailSender(ABC):
    """Port for sending one transactional email. Concrete adapters
    (Resend, SendGrid, Mailgun, SMTP, ...) live in infrastructure/email/
    and implement this without any service ever importing them directly.
    """

    @abstractmethod
    def send(self, to_email: str, to_name: str, subject: str, html_body: str) -> None:
        raise NotImplementedError
