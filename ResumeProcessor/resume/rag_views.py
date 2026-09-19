import logging

from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from rag_core.ingestion import ResumeExtractor
from rag_core.runtime import build_rag_pipeline
from rag_core.session_store import session_store

logger = logging.getLogger(__name__)

MAX_RESUME_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class UploadResumeForRAGView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        resume_file = request.FILES.get("resume")
        if not resume_file:
            return Response(
                {"error": "No resume file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if resume_file.size > MAX_RESUME_SIZE:
            return Response(
                {"error": "Resume must be 10 MB or smaller."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        suffix = "." + resume_file.name.rsplit(".", 1)[-1].lower() if "." in resume_file.name else ""
        if suffix not in ALLOWED_EXTENSIONS:
            return Response(
                {"error": "Only PDF and DOCX resumes are supported for RAG."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            text = ResumeExtractor().extract_uploaded_file(resume_file)
            if not text:
                return Response(
                    {"error": "Could not extract readable text from the resume."},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            pipeline, chunks_indexed = build_rag_pipeline(text)
            session_id = session_store.create(
                pipeline=pipeline,
                filename=resume_file.name,
                chunks_indexed=chunks_indexed,
            )

            return Response(
                {
                    "session_id": session_id,
                    "filename": resume_file.name,
                    "chunks_indexed": chunks_indexed,
                    "message": "Resume indexed successfully.",
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            logger.exception("RAG resume indexing failed.")
            return Response(
                {"error": f"Failed to index resume: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RAGChatView(APIView):
    parser_classes = [JSONParser, FormParser]

    def post(self, request):
        session_id = request.data.get("session_id")
        question = request.data.get("question")

        if not session_id or not isinstance(session_id, str):
            return Response(
                {"error": "session_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not question or not isinstance(question, str) or not question.strip():
            return Response(
                {"error": "question is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = session_store.get(session_id)
        if session is None:
            return Response(
                {"error": "Session not found or expired. Upload the resume again."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            answer, sources = session.pipeline.answer(
                question.strip(),
                chat_history=session.history[-6:],
            )

            session.history.append(
                {"role": "user", "content": question.strip()}
            )
            session.history.append(
                {"role": "assistant", "content": answer}
            )

            return Response(
                {
                    "answer": answer,
                    "sources": [
                        {
                            "score": round(score, 4),
                            "text": chunk,
                        }
                        for score, chunk in sources
                    ],
                    "filename": session.filename,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            logger.exception("RAG chat request failed.")
            return Response(
                {"error": f"Failed to generate answer: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )


class RAGSessionDeleteView(APIView):
    def delete(self, request, session_id):
        deleted = session_store.delete(session_id)
        if not deleted:
            return Response(
                {"error": "Session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
