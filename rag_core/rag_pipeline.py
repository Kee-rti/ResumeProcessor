from typing import List, Tuple

from .llm_gemini import GeminiLLM
from .prompts import SYSTEM_INSTRUCTION, build_rag_prompt
from .retrieval import Retriever


class RAGPipeline:
    """Explicit RAG pipeline: retrieve evidence, build prompt, generate answer."""

    def __init__(
        self,
        retriever: Retriever,
        llm: GeminiLLM,
        top_k: int = 3,
    ):
        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        self.retriever = retriever
        self.llm = llm
        self.top_k = top_k

    def answer(self, question: str) -> Tuple[str, List[Tuple[float, str]]]:
        retrieved_chunks = self.retriever.retrieve(
            question, top_k=self.top_k
        )
        prompt = build_rag_prompt(question, retrieved_chunks)
        answer = self.llm.generate(
            prompt,
            system_instruction=SYSTEM_INSTRUCTION,
        )
        return answer, retrieved_chunks
