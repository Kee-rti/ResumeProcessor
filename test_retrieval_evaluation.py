import numpy as np

from rag_core.evaluation import RetrievalExample, evaluate_retrieval
from rag_core.retrieval import Retriever


class FakeEmbedder:
    def embed_text(self, text: str) -> np.ndarray:
        text = text.lower()
        if "python" in text:
            return np.array([1.0, 0.0], dtype=np.float32)
        if "react" in text:
            return np.array([0.0, 1.0], dtype=np.float32)
        return np.array([0.5, 0.5], dtype=np.float32)


class FakeVectorStore:
    def __init__(self):
        self.docs = []

    def add_documents(self, chunks, embeddings):
        self.docs = list(zip(chunks, embeddings))

    def search(self, query_embedding, top_k=3):
        q = query_embedding.flatten()
        scored = []
        for chunk, vector in self.docs:
            score = float(
                np.dot(q, vector)
                / (np.linalg.norm(q) * np.linalg.norm(vector))
            )
            scored.append((score, chunk))
        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[:top_k]


def test_retrieval_evaluation_recall_at_k():
    embedder = FakeEmbedder()
    store = FakeVectorStore()
    store.add_documents(
        [
            "Python is used for backend services.",
            "React is used for frontend interfaces.",
        ],
        np.array([[1, 0], [0, 1]], dtype=np.float32),
    )

    retriever = Retriever(embedder, store)

    report = evaluate_retrieval(
        retriever,
        [
            RetrievalExample(
                "Which language is used for backend services?",
                "Python is used for backend services.",
            ),
            RetrievalExample(
                "Which library is used for frontend interfaces?",
                "React is used for frontend interfaces.",
            ),
        ],
        top_k=1,
    )

    assert report["questions"] == 2
    assert report["hits"] == 2
    assert report["recall_at_k"] == 1.0
