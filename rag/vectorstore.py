from __future__ import annotations

import logging
from typing import Dict, List, Optional

import chromadb
import google.generativeai as genai

from config import settings
from rag.embedder import GoogleEmbedder

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB wrapper using Google text-embedding-004 for RAG."""

    def __init__(self, persist_path: Optional[str] = None, embedder: Optional[GoogleEmbedder] = None) -> None:
        self.persist_path = persist_path or settings.CHROMA_DB_PATH
        self.client = chromadb.PersistentClient(path=self.persist_path)
        self.collection = self.client.get_or_create_collection(
            name="dev_docs",
            metadata={"hnsw:space": "cosine"},
        )

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.embedder = embedder or GoogleEmbedder(api_key=settings.GEMINI_API_KEY)

    def add_documents(self, documents: List[Dict]) -> None:
        """Embed and add documents with metadata to ChromaDB."""

        if not documents:
            return

        ids = [f"doc_{i}_{doc['topic']}" for i, doc in enumerate(documents)]
        texts = [doc["text"] for doc in documents]
        metadatas = [
            {
                "source": doc.get("source", "unknown"),
                "topic": doc.get("topic", "general"),
                "language": doc.get("language", "unknown"),
                "doc_type": doc.get("doc_type", "doc"),
            }
            for doc in documents
        ]

        embeddings = self.embedder.embed(texts)

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        logger.info("RAG: Added %s document chunks to ChromaDB.", len(documents))

    def query(self, topics: List[str], query_text: str, n_results: int = 5) -> Dict:
        """Semantic search with optional topic filtering."""

        query_embedding = self.embedder.embed([query_text])[0] if query_text else None
        if query_embedding is None:
            return {"context": "", "sources": [], "relevance_scores": []}

        where_filter = {"topic": {"$in": topics}} if topics else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        context_text = "\n\n".join(documents) if documents else ""
        sources = list({m.get("source", "unknown") for m in metadatas}) if metadatas else []

        return {
            "context": context_text,
            "sources": sources,
            "relevance_scores": distances,
        }

    def is_populated(self) -> bool:
        """Return True if the collection has enough content to be useful."""

        return self.collection.count() > 50
