import logging
from typing import List, Tuple

from .embeddings import Embedder
from .vector_store import NumpyVectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """Embeds questions and retrieves the most relevant indexed chunks."""

    def __init__(self, embedder: Embedder, vector_store: NumpyVectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def find_indexed_chunks(self, text: str) -> List[str]:
        """Find indexed chunks containing a labelled evidence span."""
        return self.vector_store.find_chunks_containing(text)

    def retrieve(
        self, question: str, top_k: int = 3
    ) -> List[Tuple[float, str]]:
        if not question or not question.strip():
            raise ValueError("Question must not be empty.")
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query_embedding = self.embedder.embed_text(question)
        results = self.vector_store.search(query_embedding, top_k=top_k)

        logger.info(
            "Retrieved %d chunks for question: %s",
            len(results),
            question[:100],
        )
        return results
