import logging
from typing import List, Tuple

from .embeddings import Embedder
from .vector_store import NumpyVectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """Embeds a user question and retrieves the most relevant stored chunks."""

    def __init__(self, embedder: Embedder, vector_store: NumpyVectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(
        self, question: str, top_k: int = 3
    ) -> List[Tuple[float, str]]:
        if not question or not question.strip():
            raise ValueError("Question must not be empty.")

        query_embedding = self.embedder.embed_text(question)
        results = self.vector_store.search(query_embedding, top_k=top_k)

        logger.info(
            "Retrieved %d chunks for question: %s",
            len(results),
            question[:100],
        )
        return results
