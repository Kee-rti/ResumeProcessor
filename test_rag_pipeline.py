from rag_core.rag_pipeline import RAGPipeline


class FakeRetriever:
    def retrieve(self, question, top_k=3):
        return [(0.95, "The candidate has 3 years of Python experience.")]


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
