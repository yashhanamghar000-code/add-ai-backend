from abc import ABC, abstractmethod


class IEmailVerifier(ABC):
    """Port for telling a real, deliverable mailbox apart from a fake /
    placeholder / dummy address typed in during testing (sam@gmail.com,
    test@test.com, asdf@asdf.com, ...).

    Concrete adapters live in infrastructure/email/ (e.g. an AbstractAPI
    call). Services never import the adapter directly — only this
    interface — so swapping AbstractAPI for ZeroBounce/Hunter/whatever
    is a one-line change in container.py.
    """

    @abstractmethod
    def is_real(self, email: str) -> bool:
        """Return True if `email` looks like a genuine, deliverable
        mailbox; False if it looks dummy/disposable/undeliverable.

        Implementations MUST fail *open* (return True) on network errors
        or missing API keys — verification only gates whether a
        notification email gets sent, it must never be able to block
        registration or login itself.
        """
        raise NotImplementedError
