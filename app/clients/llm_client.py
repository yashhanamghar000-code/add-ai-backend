from typing import List, Tuple

import httpx

from add_ai_core.interfaces.llm_client import ILLMClient


class LlmServiceClient(ILLMClient):

    def __init__(self, base_url: str, timeout: float = 120.0):
        # Chat completions can legitimately take a while — a much longer
        # timeout than the other, smaller adapter calls.
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def complete(self, messages: List[Tuple[str, str]]) -> str:
        payload = {"messages": [{"role": role, "content": content} for role, content in messages]}
        r = self._client.post("/complete", json=payload)
        r.raise_for_status()
        return r.json()["text"]
