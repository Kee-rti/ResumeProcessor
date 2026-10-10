import os
from functools import lru_cache

from .chunking import TextChunker
from .embeddings import Embedder
from .llm_gemini import GeminiLLM
from .rag_pipeline import RAGPipeline
from .retrieval import Retriever
from .vector_store import NumpyVectorStore


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    """Load the expensive embedding model once per application process."""
    return Embedder()


@lru_cache(maxsize=1)
def get_llm() -> GeminiLLM:
    """Reuse one Gemini client per application process."""
    return GeminiLLM()


def build_rag_pipeline(text: str, top_k: int = 3) -> tuple[RAGPipeline, int]:
    """
    Build a fresh, session-specific RAG pipeline from one resume.

    The embedding model and Gemini client are shared resources; the vector
    store and retrieved document corpus are unique to this session.
    """
    if not text or not text.strip():
        raise ValueError("Resume text is empty.")

    raw_threshold = os.getenv("RAG_MIN_SIMILARITY_SCORE", "0.45").strip()
    try:
        min_similarity_score = float(raw_threshold or "0.45")
    except ValueError as exc:
        raise ValueError(
            "RAG_MIN_SIMILARITY_SCORE must be a number between -1 and 1."
        ) from exc

    if not -1.0 <= min_similarity_score <= 1.0:
        raise ValueError("RAG_MIN_SIMILARITY_SCORE must be between -1 and 1.")

    chunker = TextChunker()
    chunks = chunker.chunk_text(text)
    if not chunks:
        raise ValueError("No usable text chunks were produced from the resume.")

    embedder = get_embedder()
    embeddings = embedder.embed_chunks(chunks)

    vector_store = NumpyVectorStore()
    vector_store.add_documents(chunks, embeddings)

    retriever = Retriever(embedder, vector_store)
    pipeline = RAGPipeline(
        retriever,
        get_llm(),
        top_k=top_k,
        min_similarity_score=min_similarity_score,
    )

    return pipeline, len(chunks)
