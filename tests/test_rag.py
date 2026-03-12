import pytest
from unittest.mock import MagicMock, patch

from rag.vectorstore import VectorStore


def test_rag_retrieval_logic():
    """Verifies RAG without calling external embed APIs."""

    mock_vector = [0.1] * 768

    with patch("rag.vectorstore.genai.embed_content") as mock_embed:
        mock_embed.return_value = {"embedding": [mock_vector]}

        db = VectorStore(persist_path="./data/test_db_tmp")

        test_docs = [
            {
                "text": "FastAPI uses Pydantic for validation.",
                "source": "https://fastapi.tiangolo.com",
                "topic": "fastapi",
                "language": "python",
                "doc_type": "tutorial",
            }
        ]

        db.add_documents(test_docs)

        results = db.query(topics=["fastapi"], query_text="How does FastAPI work?")

        assert "FastAPI" in results["context"]
        assert results["sources"][0] == "https://fastapi.tiangolo.com"
