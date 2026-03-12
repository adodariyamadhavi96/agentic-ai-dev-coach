from __future__ import annotations

import logging
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from rich.progress import Progress

logger = logging.getLogger(__name__)


class DocLoader:
    """Fetches, cleans, and chunks documentation for RAG ingestion."""

    def __init__(self) -> None:
        self.headers = {"User-Agent": "Mozilla/5.0 (Agentic-AI-Dev-Coach/1.0)"}

    def fetch_page(self, url: str) -> str:
        """Fetch HTML and strip noisy elements like nav, footer, scripts."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            for element in soup(["nav", "footer", "header", "aside", "script", "style"]):
                element.decompose()

            return soup.get_text(separator=" ", strip=True)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to fetch %s: %s", url, exc)
            return ""

    def chunk_text(self, text: str, source_meta: Dict, chunk_size: int = 800, overlap: int = 100) -> List[Dict]:
        """Split text into overlapping chunks preserving context with metadata."""

        chunks: List[Dict] = []
        words = text.split()

        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i : i + chunk_size]
            chunk_doc = source_meta.copy()
            chunk_doc["text"] = " ".join(chunk_words)
            chunks.append(chunk_doc)

        return chunks

    def load_sources(self, sources: List[Dict], progress: Progress | None = None, task_id=None) -> List[Dict]:
        """Fetch and chunk all sources, updating a progress task if provided."""

        all_chunks: List[Dict] = []
        for source in sources:
            url = source["url"]
            if progress and task_id is not None:
                progress.console.print(f"Scraping: {url}")

            raw_text = self.fetch_page(url)
            if raw_text:
                all_chunks.extend(self.chunk_text(raw_text, source))

            if progress and task_id is not None:
                progress.update(task_id, advance=1)

        return all_chunks
