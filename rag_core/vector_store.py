import logging
from typing import List, Tuple

import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NumpyVectorStore:
    """
    A simple vector store using NumPy arrays.

    Stores text chunks alongside their pre-computed embedding vectors.
    """

    def __init__(self):
        self.chunks: List[str] = []
        self.embeddings: np.ndarray = None

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize case and whitespace for exact evidence-span matching."""
        return " ".join(text.casefold().split())

    def find_chunks_containing(self, text: str) -> List[str]:
        """
        Find indexed chunks containing a labelled evidence span.

        The entire normalized span must occur within one chunk. This also
        supports gold passages that are shorter than the chunks produced by
        the configured chunker.
        """
        normalized_text = self._normalize_text(text)
        if not normalized_text:
            return []

        return [
            chunk
            for chunk in self.chunks
            if normalized_text in self._normalize_text(chunk)
        ]

    def contains_chunk(self, text: str) -> bool:
        """Return whether a labelled evidence span exists in the index."""
        return bool(self.find_chunks_containing(text))

    def add_documents(self, chunks: List[str], embeddings: np.ndarray):
        """Add chunks and their pre-computed embeddings to the store."""
        if len(chunks) != embeddings.shape[0]:
            raise ValueError("Number of chunks must match number of embeddings.")

        if self.embeddings is None:
            self.embeddings = embeddings
            self.chunks = list(chunks)
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])
            self.chunks.extend(chunks)

        logger.info(
            "Added %d documents. Total in store: %d.",
            len(chunks),
            len(self.chunks),
        )

    def search(
        self, query_embedding: np.ndarray, top_k: int = 3
    ) -> List[Tuple[float, str]]:
        """
        Calculate cosine similarity against all stored embeddings.

        Returns the top-k chunks with their similarity scores.
        """
        if self.embeddings is None or len(self.chunks) == 0:
            logger.warning("Vector store is empty.")
            return []

        query_vec = query_embedding.flatten()
        dot_products = np.dot(self.embeddings, query_vec)
        query_norm = np.linalg.norm(query_vec)
        embeddings_norms = np.linalg.norm(self.embeddings, axis=1)
        similarities = dot_products / (query_norm * embeddings_norms + 1e-10)

        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [
            (float(similarities[idx]), self.chunks[idx])
            for idx in top_indices
        ]
