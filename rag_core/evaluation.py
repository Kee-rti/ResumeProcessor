from dataclasses import dataclass
from typing import List

from .retrieval import Retriever


@dataclass(frozen=True)
class RetrievalExample:
    question: str
    relevant_chunk: str


def evaluate_retrieval(
    retriever: Retriever,
    examples: List[RetrievalExample],
    top_k: int = 3,
) -> dict:
    """Evaluate whether the expected chunk is returned in the top-k results."""
    if not examples:
        raise ValueError("examples must not be empty")
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    hits = 0
    results = []

    for example in examples:
        retrieved = retriever.retrieve(example.question, top_k=top_k)
        chunks = [chunk for _, chunk in retrieved]

        hit = example.relevant_chunk in chunks
        if hit:
            hits += 1

        results.append(
            {
                "question": example.question,
                "relevant_chunk": example.relevant_chunk,
                "retrieved_chunks": chunks,
                "hit": hit,
                "scores": [round(score, 4) for score, _ in retrieved],
            }
        )

    return {
        "questions": len(examples),
        "hits": hits,
        "recall_at_k": hits / len(examples),
        "results": results,
    }
