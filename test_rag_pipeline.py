import pytest

from rag_core.prompts import INSUFFICIENT_EVIDENCE_RESPONSE
from rag_core.rag_pipeline import RAGPipeline


class FakeRetriever:
    def __init__(self, results=None):
        self.results = (
            results
            if results is not None
            else [(0.95, "The candidate has 3 years of Python experience.")]
        )

    def retrieve(self, question, top_k=3):
        return self.results


class FakeLLM:
    def __init__(self):
        self.prompt = None
        self.system_instruction = None

    def generate(self, prompt, system_instruction=None):
        self.prompt = prompt
        self.system_instruction = system_instruction
        return "The candidate has 3 years of Python experience."


def test_rag_pipeline_connects_retrieval_prompt_and_generation():
    retriever = FakeRetriever()
    llm = FakeLLM()

    pipeline = RAGPipeline(retriever, llm, top_k=3)
    answer, retrieved = pipeline.answer("How much Python experience does the candidate have?")

    assert answer == "The candidate has 3 years of Python experience."
    assert retrieved == [(0.95, "The candidate has 3 years of Python experience.")]
    assert "How much Python experience" in llm.prompt
    assert "3 years of Python experience" in llm.prompt
    assert "untrusted data" in llm.system_instruction


def test_pipeline_abstains_when_no_chunks_are_retrieved():
    llm = FakeLLM()
    pipeline = RAGPipeline(FakeRetriever([]), llm, min_similarity_score=0.45)

    answer, sources = pipeline.answer("What is the candidate's AWS experience?")

    assert answer == INSUFFICIENT_EVIDENCE_RESPONSE
    assert sources == []
    assert llm.prompt is None


def test_pipeline_abstains_when_all_chunks_are_below_threshold():
    llm = FakeLLM()
    retriever = FakeRetriever([(0.44, "A weakly related resume chunk.")])
    pipeline = RAGPipeline(retriever, llm, min_similarity_score=0.45)

    answer, sources = pipeline.answer("What is the candidate's AWS experience?")

    assert answer == INSUFFICIENT_EVIDENCE_RESPONSE
    assert sources == []
    assert llm.prompt is None


def test_pipeline_only_passes_chunks_that_clear_threshold():
    llm = FakeLLM()
    retriever = FakeRetriever([
        (0.82, "Built ML systems using Python."),
        (0.31, "Unrelated education detail."),
    ])
    pipeline = RAGPipeline(retriever, llm, min_similarity_score=0.45)

    _, sources = pipeline.answer("What Python experience does the candidate have?")

    assert "Built ML systems using Python." in llm.prompt
    assert "Unrelated education detail." not in llm.prompt
    assert sources == [(0.82, "Built ML systems using Python.")]


@pytest.mark.parametrize("threshold", [-1.01, 1.01, float("inf"), float("nan")])
def test_pipeline_rejects_invalid_similarity_thresholds(threshold):
    with pytest.raises(ValueError, match="between -1 and 1"):
        RAGPipeline(FakeRetriever(), FakeLLM(), min_similarity_score=threshold)
