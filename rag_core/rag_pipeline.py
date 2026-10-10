import math
from typing import List, Tuple

from .llm_gemini import GeminiLLM
from .prompts import (
    INSUFFICIENT_EVIDENCE_RESPONSE,
    SYSTEM_INSTRUCTION,
    build_rag_prompt,
)
from .retrieval import Retriever


class RAGPipeline:
    """Retrieve evidence, abstain on weak matches, then generate a grounded answer."""

    def __init__(
        self,
        retriever: Retriever,
        llm: GeminiLLM,
        top_k: int = 3,
        min_similarity_score: float = 0.45,
    ):
        if top_k <= 0:
            raise ValueError("top_k must be positive.")
        if (
            not math.isfinite(min_similarity_score)
            or not -1.0 <= min_similarity_score <= 1.0
        ):
            raise ValueError("min_similarity_score must be between -1 and 1.")

        self.retriever = retriever
        self.llm = llm
        self.top_k = top_k
        self.min_similarity_score = min_similarity_score

    def answer(
        self,
        question: str,
        chat_history: List[dict] | None = None,
    ) -> Tuple[str, List[Tuple[float, str]]]:
        retrieved_chunks = self.retriever.retrieve(question, top_k=self.top_k)
        supported_chunks = [
            (score, chunk)
            for score, chunk in retrieved_chunks
            if score >= self.min_similarity_score
        ]

        # Do not ask the LLM to answer from weak or missing retrieval evidence.
        if not supported_chunks:
            return INSUFFICIENT_EVIDENCE_RESPONSE, []

        prompt = build_rag_prompt(
            question,
            supported_chunks,
            chat_history=chat_history or [],
        )
        answer = self.llm.generate(
            prompt,
            system_instruction=SYSTEM_INSTRUCTION,
        )
        return answer, supported_chunks
