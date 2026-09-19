import numpy as np

from rag_core.retrieval import Retriever


class FakeEmbedder:
    """Deterministic embeddings so retrieval can be tested without a model."""

    def embed_text(self, text: str) -> np.ndarray:
        if "python" in text.lower():
            return np.array([1.0, 0.0], dtype=np.float32)
        return np.array([0.0, 1.0], dtype=np.float32)


class FakeVectorStore:
    def __init__(self):
        self.last_query = None
        self.last_top_k = None

    def search(self, query_embedding, top_k=3):
        self.last_query = query_embedding
        self.last_top_k = top_k
        return [(0.91, "Python chunk")]


def test_retriever_embeds_query_and_searches():
    embedder = FakeEmbedder()
    store = FakeVectorStore()
    retriever = Retriever(embedder, store)

    results = retriever.retrieve("What Python experience does the candidate have?", top_k=2)

    assert results == [(0.91, "Python chunk")]
    assert store.last_top_k == 2
    assert np.array_equal(store.last_query, np.array([1.0, 0.0], dtype=np.float32))
