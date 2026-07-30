from typing import List

import httpx

from add_ai_core.entities.document import DocumentChunk
from add_ai_core.interfaces.reranker import IReranker


class RerankerServiceClient(IReranker):

    def __init__(self, base_url: str, timeout: float = 30.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def rerank(self, query: str, candidates: List[DocumentChunk], top_n: int) -> List[DocumentChunk]:
        if not candidates:
            return []
        payload = {
            "query": query,
            "candidates": [{"content": c.content, "metadata": c.metadata} for c in candidates],
            "top_n": top_n,
        }
        r = self._client.post("/rerank", json=payload)
        r.raise_for_status()
        return [DocumentChunk(content=c["content"], metadata=c["metadata"]) for c in r.json()["results"]]
