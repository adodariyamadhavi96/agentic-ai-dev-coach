from __future__ import annotations
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.doc_loader import DocLoader
from rag.sources import DOC_SOURCES
from rag.vectorstore import VectorStore
from utils.logger import get_logger
from rich.console import Console
from rich.progress import Progress

logger = get_logger("setup_rag")
console = Console()


def main() -> None:
    db = VectorStore()
    loader = DocLoader()

    if db.is_populated():
        console.print("[yellow]RAG Database already populated. Skipping...[/yellow]")
        return

    with Progress() as progress:
        task = progress.add_task("[cyan]Indexing documentation...", total=len(DOC_SOURCES))
        chunks = loader.load_sources(DOC_SOURCES, progress=progress, task_id=task)
        if chunks:
            # Embed once to warm up and validate keys
            logger.info("Embedding first chunk for validation")
            db.embedder.embed([chunks[0]["text"]])
            db.add_documents(chunks)

    console.print("[bold green]✅ RAG Setup Complete. Your Coach is now grounded in real docs![/bold green]")


if __name__ == "__main__":
    main()
