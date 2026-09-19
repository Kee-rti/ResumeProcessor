import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List

from .rag_pipeline import RAGPipeline


@dataclass
class RAGSession:
    """Ephemeral, process-local state for one uploaded resume."""
    pipeline: RAGPipeline
    filename: str
    chunks_indexed: int
    history: List[dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)


class RAGSessionStore:
    """
    In-memory session registry for V1.

    Each session owns its RAG pipeline/vector store and chat history.
    Sessions expire automatically. This is intentionally ephemeral:
    no resume text, embeddings, or FAISS/NumPy indexes are persisted.

    This registry is process-local. A multi-worker production deployment
    should replace it with a shared cache such as Redis.
    """

    def __init__(self, ttl_seconds: int = 3600, max_sessions: int = 100):
        if ttl_seconds <= 0 or max_sessions <= 0:
            raise ValueError("ttl_seconds and max_sessions must be positive.")

        self.ttl_seconds = ttl_seconds
        self.max_sessions = max_sessions
        self._sessions: Dict[str, RAGSession] = {}
        self._lock = threading.RLock()

    def _cleanup_expired(self) -> None:
        now = time.time()
        expired = [
            session_id
            for session_id, session in self._sessions.items()
            if now - session.last_accessed > self.ttl_seconds
        ]
        for session_id in expired:
            del self._sessions[session_id]

    def create(self, pipeline: RAGPipeline, filename: str, chunks_indexed: int) -> str:
        with self._lock:
            self._cleanup_expired()

            if len(self._sessions) >= self.max_sessions:
                oldest_id = min(
                    self._sessions,
                    key=lambda sid: self._sessions[sid].last_accessed,
                )
                del self._sessions[oldest_id]

            session_id = uuid.uuid4().hex
            self._sessions[session_id] = RAGSession(
                pipeline=pipeline,
                filename=filename,
                chunks_indexed=chunks_indexed,
            )
            return session_id

    def get(self, session_id: str) -> RAGSession | None:
        if not session_id:
            return None

        with self._lock:
            self._cleanup_expired()
            session = self._sessions.get(session_id)
            if session is not None:
                session.last_accessed = time.time()
            return session

    def delete(self, session_id: str) -> bool:
        with self._lock:
            return self._sessions.pop(session_id, None) is not None


session_store = RAGSessionStore()
