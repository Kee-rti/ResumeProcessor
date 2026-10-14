import math


DEFAULT_MIN_SIMILARITY_SCORE = 0.45


def parse_min_similarity_score(raw_value: str | None) -> float:
    """Parse and validate a cosine-similarity cutoff from configuration."""
    if raw_value is None or not raw_value.strip():
        return DEFAULT_MIN_SIMILARITY_SCORE

    try:
        score = float(raw_value)
    except ValueError as exc:
        raise ValueError(
            "RAG_MIN_SIMILARITY_SCORE must be a number between -1 and 1."
        ) from exc

    if not math.isfinite(score) or not -1.0 <= score <= 1.0:
        raise ValueError(
            "RAG_MIN_SIMILARITY_SCORE must be a finite number between -1 and 1."
        )

    return score
