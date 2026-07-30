from typing import List

import httpx

from add_ai_core.interfaces.embedding_provider import IEmbeddingProvider


class EmbeddingServiceClient(IEmbeddingProvider):
    """Implements IEmbeddingProvider over HTTP against add-ai-embeddings-service.
    Everything upstream of this class (RetrievalService, IngestionService)
    still just calls `.embed_documents()` / `.embed_query()` — it has no
    idea the 'adapter' now makes a network call instead of an in-process
    model call. That's the whole point of depending on the interface."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        r = self._client.post("/embed/documents", json={"texts": texts})
        r.raise_for_status()
        return r.json()["vectors"]

    def embed_query(self, text: str) -> List[float]:
        r = self._client.post("/embed/query", json={"text": text})
        r.raise_for_status()
        return r.json()["vector"]
