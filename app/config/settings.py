import os
from dataclasses import dataclass, field


def _env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)


def _env_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    return int(raw) if raw is not None else default


@dataclass(frozen=True)
class Settings:
    # Every other adapter is now a network call, not an import — this is
    # the platform's service registry, hard-coded to env vars so it's set
    # once, in the orchestration compose file, and never touched here.
    embeddings_service_url: str = field(default_factory=lambda: _env("EMBEDDINGS_SERVICE_URL", "http://embeddings-service:8001"))
    reranker_service_url: str = field(default_factory=lambda: _env("RERANKER_SERVICE_URL", "http://reranker-service:8002"))
    llm_service_url: str = field(default_factory=lambda: _env("LLM_SERVICE_URL", "http://llm-service:8003"))
    vectorstore_service_url: str = field(default_factory=lambda: _env("VECTORSTORE_SERVICE_URL", "http://vectorstore-service:8004"))
    sparseindex_service_url: str = field(default_factory=lambda: _env("SPARSEINDEX_SERVICE_URL", "http://sparseindex-service:8005"))
    data_service_url: str = field(default_factory=lambda: _env("DATA_SERVICE_URL", "http://data-service:8007"))
    auth_service_url: str = field(default_factory=lambda: _env("AUTH_SERVICE_URL", "http://auth-service:8008"))

    top_k_per_query: int = field(default_factory=lambda: _env_int("TOP_K_PER_QUERY", 15))
    final_docs_per_query: int = field(default_factory=lambda: _env_int("FINAL_DOCS_PER_QUERY", 6))
    max_total_context_docs: int = field(default_factory=lambda: _env_int("MAX_TOTAL_CONTEXT_DOCS", 18))

    storage_dir: str = field(default_factory=lambda: _env("STORAGE_DIR", "./storage"))
    temp_upload_dir: str = field(default_factory=lambda: _env("TEMP_UPLOAD_DIR", "./temp_uploads"))

    redis_url: str = field(default_factory=lambda: _env("REDIS_URL", "redis://redis:6379/0"))

    # --- Notification emails (welcome-on-signup / alert-on-login) ---
    # Real-vs-dummy detection: AbstractAPI Email Validation.
    # https://app.abstractapi.com/api/email-verification/
    abstract_api_key: str | None = field(default_factory=lambda: _env("ABSTRACT_API_KEY"))
    # Sending: Resend transactional email API. https://resend.com
    resend_api_key: str | None = field(default_factory=lambda: _env("RESEND_API_KEY"))
    mail_from_email: str = field(default_factory=lambda: _env("MAIL_FROM_EMAIL", "onboarding@resend.dev"))
    mail_from_name: str = field(default_factory=lambda: _env("MAIL_FROM_NAME", "AUDITO AI"))
    app_name: str = field(default_factory=lambda: _env("APP_NAME", "AUDITO AI"))
    app_logo_url: str | None = field(default_factory=lambda: _env("APP_LOGO_URL"))
    frontend_url: str = field(default_factory=lambda: _env("FRONTEND_URL", "http://localhost:3000"))

    def ensure_directories(self) -> None:
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(self.temp_upload_dir, exist_ok=True)


settings = Settings()
