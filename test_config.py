import pytest

from rag_core.config import DEFAULT_MIN_SIMILARITY_SCORE, parse_min_similarity_score


def test_missing_or_blank_threshold_uses_default():
    assert parse_min_similarity_score(None) == DEFAULT_MIN_SIMILARITY_SCORE
    assert parse_min_similarity_score("") == DEFAULT_MIN_SIMILARITY_SCORE
    assert parse_min_similarity_score("   ") == DEFAULT_MIN_SIMILARITY_SCORE


def test_valid_threshold_is_parsed():
    assert parse_min_similarity_score("0.62") == 0.62
    assert parse_min_similarity_score("-0.2") == -0.2
    assert parse_min_similarity_score("1") == 1.0


@pytest.mark.parametrize(
    "raw_value",
    ["not-a-number", "nan", "inf", "-inf", "1.01", "-1.01"],
)
def test_invalid_threshold_is_rejected(raw_value):
    with pytest.raises(ValueError, match="RAG_MIN_SIMILARITY_SCORE"):
        parse_min_similarity_score(raw_value)
