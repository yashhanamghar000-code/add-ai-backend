"""
Composition root for add-ai-backend. The ONE difference from the original
monolith's container.py: every adapter is now an HTTP-client class
pointed at another repo's service URL, instead of an in-process object
constructed with a model path or a DB session. `services/` — copied here
unmodified — has no idea the difference; it still only ever calls
interface methods like `.embed_query()` or `.search()`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.clients.data_client import (
    ChatMessageRepositoryClient, ConversationRepositoryClient, FileRepositoryClient,
)
from app.clients.embedding_client import EmbeddingServiceClient
from app.clients.llm_client import LlmServiceClient
from app.clients.reranker_client import RerankerServiceClient
from app.clients.sparseindex_client import SparseIndexServiceClient
from app.clients.vectorstore_client import VectorStoreServiceClient
from app.config.settings import Settings, settings as default_settings
from app.infrastructure.email.abstract_api_email_verifier import AbstractApiEmailVerifier
from app.infrastructure.email.resend_email_sender import ResendEmailSender
from app.services.chat_workflow_service import ChatWorkflowService
from app.services.history_service import HistoryService
from app.services.notification_service import NotificationService
from app.services.retrieval_service import RetrievalService
from app.services.session_service import SessionService


class SharedSingletons:
    """HTTP clients are cheap (no model to load, just a connection pool),
    but still built once per process and shared — same shape as the
    original monolith's SharedSingletons, for the same reason: avoid
    re-creating a client per request."""

    def __init__(self, cfg: Settings):
        cfg.ensure_directories()

        self.embedding_provider = EmbeddingServiceClient(cfg.embeddings_service_url)
        self.reranker = RerankerServiceClient(cfg.reranker_service_url)
        self.llm_client = LlmServiceClient(cfg.llm_service_url)
        self.vector_store = VectorStoreServiceClient(cfg.vectorstore_service_url)
        self.sparse_index = SparseIndexServiceClient(cfg.sparseindex_service_url)

        self.conversation_repo = ConversationRepositoryClient(cfg.data_service_url)
        self.chat_message_repo = ChatMessageRepositoryClient(cfg.data_service_url)
        self.file_repo = FileRepositoryClient(cfg.data_service_url)

        self.retrieval_service = RetrievalService(
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
            sparse_index=self.sparse_index,
            reranker=self.reranker,
        )
        self.chat_workflow_service = ChatWorkflowService(
            llm_client=self.llm_client,
            retrieval_service=self.retrieval_service,
            top_k_per_query=cfg.top_k_per_query,
            final_docs_per_query=cfg.final_docs_per_query,
            max_total_context_docs=cfg.max_total_context_docs,
        )

        self.email_verifier = AbstractApiEmailVerifier(api_key=cfg.abstract_api_key)
        self.email_sender = ResendEmailSender(
            api_key=cfg.resend_api_key,
            from_email=cfg.mail_from_email,
            from_name=cfg.mail_from_name,
        )
        self.notification_service = NotificationService(
            email_verifier=self.email_verifier,
            email_sender=self.email_sender,
            app_name=cfg.app_name,
            app_logo_url=cfg.app_logo_url,
            frontend_url=cfg.frontend_url,
        )


@dataclass
class Container:
    history_service: HistoryService
    session_service: SessionService
    chat_workflow_service: ChatWorkflowService
    notification_service: NotificationService


_singletons: Optional[SharedSingletons] = None


def _get_singletons(cfg: Settings) -> SharedSingletons:
    global _singletons
    if _singletons is None:
        print("[Container] Booting shared HTTP clients for embeddings/reranker/llm/vectorstore/sparseindex/data...")
        _singletons = SharedSingletons(cfg)
        print("[Container] Shared clients ready.")
    return _singletons


def build_container(cfg: Settings = default_settings) -> Container:
    """No DB session to scope this to anymore — every repository is now
    an HTTP client. Still cheap to call once per request, same as before."""
    shared = _get_singletons(cfg)

    return Container(
        history_service=HistoryService(shared.conversation_repo, shared.chat_message_repo, shared.file_repo),
        session_service=SessionService(shared.vector_store, shared.sparse_index, shared.conversation_repo, shared.file_repo),
        chat_workflow_service=shared.chat_workflow_service,
        notification_service=shared.notification_service,
    )
