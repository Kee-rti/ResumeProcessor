from typing import List, Tuple

from .retrieval import Retriever


def evaluate_retrieval(
    retriever: Retriever,
    questions: List[Tuple[str, List[str]]],
    top_k: int = 3,
) -> dict:
    """
    Evaluate retrieval against a tiny hand-labelled test set.

    questions:
      [(question, [expected_substring_1, ...]), ...]
    """
    if not questions:
        raise ValueError("questions must not be empty")

    passed = 0
    results = []

    for question, expected_terms in questions:
        retrieved = retriever.retrieve(question, top_k=top_k)
        retrieved_text = "
".join(chunk.lower() for _, chunk in retrieved)

        hit = bool(expected_terms) and all(
            term.lower() in retrieved_text for term in expected_terms
        )

        results.append(
            {
                "question": question,
                "expected_terms": expected_terms,
                "hit": hit,
                "scores": [round(score, 4) for score, _ in retrieved],
            }
        )

        passed += int(hit)

    return {
        "questions": len(questions),
        "passed": passed,
        "retrieval_hit_rate": passed / len(questions),
        "results": results,
    }
