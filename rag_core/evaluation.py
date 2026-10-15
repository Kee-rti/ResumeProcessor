from dataclasses import dataclass
from typing import List

from .retrieval import Retriever


@dataclass(frozen=True)
class RetrievalExample:
    question: str
    relevant_chunk: str


def _normalize_text(text: str) -> str:
    """Normalize case and whitespace when matching gold evidence to chunks."""
    return " ".join(text.casefold().split())


def evaluate_retrieval(
    retriever: Retriever,
    examples: List[RetrievalExample],
    top_k: int = 3,
) -> dict:
    """
    Measure Recall@k and diagnose whether missed gold evidence is indexed.

    Diagnosis values:
    - retrieved_in_top_k: the gold evidence appears within a returned chunk
    - indexed_but_missed_top_k: evidence exists in the index, but not top-k
    - not_in_index: no indexed chunk contains the labelled evidence span

    A gold evidence span must fit inside one indexed chunk for this diagnostic
    to count it as indexed. If chunking splits a labelled span across chunks,
    this points to a likely ingestion/chunking mismatch.
    """
    if not examples:
        raise ValueError("examples must not be empty")
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    diagnosis_counts = {
        "retrieved_in_top_k": 0,
        "indexed_but_missed_top_k": 0,
        "not_in_index": 0,
    }
    results = []

    for example in examples:
        retrieved = retriever.retrieve(example.question, top_k=top_k)
        retrieved_chunks = [chunk for _, chunk in retrieved]
        normalized_gold = _normalize_text(example.relevant_chunk)

        hit = bool(normalized_gold) and any(
            normalized_gold in _normalize_text(chunk)
            for chunk in retrieved_chunks
        )
        indexed_matches = retriever.find_indexed_chunks(example.relevant_chunk)

        if hit:
            diagnosis = "retrieved_in_top_k"
        elif indexed_matches:
            diagnosis = "indexed_but_missed_top_k"
        else:
            diagnosis = "not_in_index"

        diagnosis_counts[diagnosis] += 1
        results.append(
            {
                "question": example.question,
                "relevant_chunk": example.relevant_chunk,
                "retrieved_chunks": retrieved_chunks,
                "hit": hit,
                "scores": [round(score, 4) for score, _ in retrieved],
                "diagnosis": diagnosis,
                "indexed_matches": indexed_matches,
            }
        )

    hits = diagnosis_counts["retrieved_in_top_k"]
    return {
        "questions": len(examples),
        "hits": hits,
        "recall_at_k": hits / len(examples),
        "diagnosis_counts": diagnosis_counts,
        "results": results,
    }
