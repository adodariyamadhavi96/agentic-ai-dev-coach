from __future__ import annotations

import logging
import time
from typing import List

import google.generativeai as genai

logger = logging.getLogger(__name__)


class GoogleEmbedder:
    """Wrapper around Google text-embedding-004 with simple caching and backoff."""

    def __init__(self, api_key: str) -> None:
        genai.configure(api_key=api_key)
        self.model = "models/gemini-embedding-001"
        self._cache: dict[str, List[float]] = {}

    def embed(self, texts: List[str]) -> List[List[float]]:
        results: List[List[float]] = []
        batch_size = 100

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            uncached = [t for t in batch if t not in self._cache]

            if uncached:
                try:
                    response = genai.embed_content(
                        model=self.model,
                        content=uncached,
                        task_type="retrieval_document",
                    )
                    embeddings = response["embedding"]
                    for text, vec in zip(uncached, embeddings):
                        self._cache[text] = vec
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Embedding rate limit hit, retrying... %s", exc)
                    time.sleep(2)
                    return self.embed(texts)

            results.extend([self._cache[t] for t in batch])

        return results
