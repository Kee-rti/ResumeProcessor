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

    def find_chunks_containing(self, text):
        normalized_text = " ".join(text.casefold().split())
        if not normalized_text:
            return []
        return [
            chunk
            for chunk, _ in self.docs
            if normalized_text in " ".join(chunk.casefold().split())
        ]

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


def _make_retriever():
    embedder = FakeEmbedder()
    store = FakeVectorStore()
    store.add_documents(
        [
            "Python is used for backend services.",
            "React is used for frontend interfaces.",
        ],
        np.array([[1, 0], [0, 1]], dtype=np.float32),
    )
    return Retriever(embedder, store)


def test_retrieval_evaluation_recall_at_k():
    report = evaluate_retrieval(
        _make_retriever(),
        [
            RetrievalExample(
                "Which language is used for Python backend services?",
                "Python is used for backend services.",
            ),
            RetrievalExample(
                "Which library is used for React frontend interfaces?",
                "React is used for frontend interfaces.",
            ),
        ],
        top_k=1,
    )

    assert report["questions"] == 2
    assert report["hits"] == 2
    assert report["recall_at_k"] == 1.0
    assert report["diagnosis_counts"] == {
        "retrieved_in_top_k": 2,
        "indexed_but_missed_top_k": 0,
        "not_in_index": 0,
    }


def test_diagnosis_detects_gold_evidence_missing_from_index():
    report = evaluate_retrieval(
        _make_retriever(),
        [
            RetrievalExample(
                "What AWS experience does the candidate have?",
                "Candidate deployed services on AWS.",
            )
        ],
        top_k=1,
    )

    result = report["results"][0]
    assert result["hit"] is False
    assert result["diagnosis"] == "not_in_index"
    assert result["indexed_matches"] == []
    assert report["diagnosis_counts"]["not_in_index"] == 1


def test_diagnosis_detects_gold_evidence_indexed_but_outside_top_k():
    report = evaluate_retrieval(
        _make_retriever(),
        [
            RetrievalExample(
                "What Python backend experience does the candidate have?",
                "React is used for frontend interfaces.",
            )
        ],
        top_k=1,
    )

    result = report["results"][0]
    assert result["hit"] is False
    assert result["diagnosis"] == "indexed_but_missed_top_k"
    assert result["indexed_matches"] == ["React is used for frontend interfaces."]
    assert report["diagnosis_counts"]["indexed_but_missed_top_k"] == 1


def test_gold_evidence_can_match_inside_a_larger_indexed_chunk():
    report = evaluate_retrieval(
        _make_retriever(),
        [
            RetrievalExample(
                "What Python backend experience does the candidate have?",
                "used for backend services.",
            )
        ],
        top_k=1,
    )

    result = report["results"][0]
    assert result["hit"] is True
    assert result["diagnosis"] == "retrieved_in_top_k"
