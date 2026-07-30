from typing import List, Optional

import httpx

from add_ai_core.entities.document import DocumentChunk
from add_ai_core.interfaces.sparse_index import ISparseIndex


class SparseIndexServiceClient(ISparseIndex):

    def __init__(self, base_url: str, timeout: float = 30.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def add_documents(self, user_id: str, chunks: List[DocumentChunk]) -> None:
        if not chunks:
            return
        payload = {"user_id": user_id, "chunks": [{"content": c.content, "metadata": c.metadata} for c in chunks]}
        r = self._client.post("/documents", json=payload)
        r.raise_for_status()

    def search(self, user_id: str, query: str, top_k: int, file_ids: Optional[List[str]] = None) -> List[DocumentChunk]:
        payload = {"user_id": user_id, "query": query, "top_k": top_k, "file_ids": file_ids}
        r = self._client.post("/search", json=payload)
        r.raise_for_status()
        return [DocumentChunk(content=c["content"], metadata=c["metadata"]) for c in r.json()["results"]]

    def remove_file(self, user_id: str, file_id: str) -> None:
        r = self._client.delete(f"/file/{user_id}/{file_id}")
        r.raise_for_status()
