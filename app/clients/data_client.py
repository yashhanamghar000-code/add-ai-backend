"""
HTTP-client implementations of the repository interfaces from add-ai-core,
calling add-ai-data-service instead of touching SQLAlchemy directly.
Where the original SQLAlchemy repos returned ORM model instances, these
return `types.SimpleNamespace` objects with the same attribute names, so
`services/history_service.py` and `services/session_service.py` — copied
here verbatim from the monolith — don't need to change a single line.
"""
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import httpx

from add_ai_core.interfaces.repositories import (
    IChatMessageRepository, IConversationRepository, IFileRepository,
)


class ConversationRepositoryClient(IConversationRepository):

    def __init__(self, base_url: str, timeout: float = 15.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def get_or_create(self, user_id: int, session_id: str, title_hint: str) -> Any:
        r = self._client.post("/conversations/get-or-create", json={
            "user_id": user_id, "session_id": session_id, "title_hint": title_hint,
        })
        if r.status_code == 403:
            raise PermissionError(r.json().get("detail", "session_id belongs to a different user"))
        r.raise_for_status()
        return SimpleNamespace(**r.json())

    def list_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        r = self._client.get("/conversations", params={"user_id": user_id})
        r.raise_for_status()
        return r.json()

    def delete(self, user_id: int, session_id: str) -> None:
        r = self._client.delete(f"/conversations/{session_id}", params={"user_id": user_id})
        r.raise_for_status()


class ChatMessageRepositoryClient(IChatMessageRepository):

    def __init__(self, base_url: str, timeout: float = 15.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def save_turn(self, user_id: int, session_id: str, query: str, response: str) -> None:
        r = self._client.post("/chat-messages/turn", json={
            "user_id": user_id, "session_id": session_id, "query": query, "response": response,
        })
        r.raise_for_status()

    def get_history(self, user_id: int, session_id: str) -> List[Dict[str, Any]]:
        r = self._client.get("/chat-messages/history", params={"user_id": user_id, "session_id": session_id})
        r.raise_for_status()
        return r.json()


class FileRepositoryClient(IFileRepository):

    def __init__(self, base_url: str, timeout: float = 15.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def create_pending(self, user_id: int, session_id: str, file_name: str, file_path: str) -> Any:
        r = self._client.post("/files/pending", json={
            "user_id": user_id, "session_id": session_id, "file_name": file_name, "file_path": file_path,
        })
        r.raise_for_status()
        return SimpleNamespace(**r.json())

    def update_status(self, file_id: int, status: str, total_chunks_indexed: int = 0) -> None:
        r = self._client.patch(f"/files/{file_id}/status", json={
            "status": status, "total_chunks_indexed": total_chunks_indexed,
        })
        r.raise_for_status()

    def get_owned(self, user_id: int, file_id: int) -> Optional[Any]:
        r = self._client.get(f"/files/{file_id}", params={"user_id": user_id})
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return SimpleNamespace(**r.json())

    def delete(self, user_id: int, file_id: int) -> Optional[Dict[str, Any]]:
        r = self._client.delete(f"/files/{file_id}", params={"user_id": user_id})
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    def list_for_conversation(self, user_id: int, session_id: str) -> List[Dict[str, Any]]:
        r = self._client.get("/files", params={"user_id": user_id, "session_id": session_id})
        r.raise_for_status()
        return r.json()
