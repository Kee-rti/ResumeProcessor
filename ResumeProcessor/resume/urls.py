from django.urls import path

from .views import ExtractResumeView
from .rag_views import (
    RAGChatView,
    RAGSessionDeleteView,
    UploadResumeForRAGView,
)

urlpatterns = [
    path("extract_resume/", ExtractResumeView.as_view(), name="extract_resume"),
    path("rag/upload/", UploadResumeForRAGView.as_view(), name="rag_upload"),
    path("rag/chat/", RAGChatView.as_view(), name="rag_chat"),
    path(
        "rag/session/<str:session_id>/",
        RAGSessionDeleteView.as_view(),
        name="rag_session_delete",
    ),
]
