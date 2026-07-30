from typing import List, Optional

import httpx

from add_ai_core.entities.document import DocumentChunk
from add_ai_core.interfaces.vector_store import IVectorStore


class VectorStoreServiceClient(IVectorStore):

    def __init__(self, base_url: str, timeout: float = 30.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def upsert(self, chunks: List[DocumentChunk], vectors: List[List[float]], user_id: str, session_id: str) -> None:
        payload = {
            "chunks": [{"content": c.content, "metadata": c.metadata} for c in chunks],
            "vectors": vectors,
            "user_id": user_id,
            "session_id": session_id,
        }
        r = self._client.post("/upsert", json=payload)
        r.raise_for_status()

    def search(self, query_vector: List[float], user_id: str, top_k: int, file_ids: Optional[List[str]] = None) -> List[DocumentChunk]:
        payload = {"query_vector": query_vector, "user_id": user_id, "top_k": top_k, "file_ids": file_ids}
        r = self._client.post("/search", json=payload)
        r.raise_for_status()
        return [DocumentChunk(content=c["content"], metadata=c["metadata"]) for c in r.json()["results"]]

    def delete_session(self, user_id: str, session_id: str) -> None:
        r = self._client.delete(f"/session/{user_id}/{session_id}")
        r.raise_for_status()

    def delete_file(self, user_id: str, file_id: str) -> None:
        r = self._client.delete(f"/file/{user_id}/{file_id}")
        r.raise_for_status()
