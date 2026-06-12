"""RAG 知识库模块 URL 路由"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter(trailing_slash=False)
router.register(r"kb", views.KnowledgeBaseViewSet, basename="knowledgebase")
router.register(r"documents", views.DocumentViewSet, basename="document")

urlpatterns = [
    path("", include(router.urls)),
    # POST /api/rag/kb/<kb_id>/chat
    path("kb/<int:kb_id>/chat", views.ChatView.as_view(), name="rag-chat"),
    # POST /api/rag/kb/<kb_id>/chat-stream （SSE 流式）
    path("kb/<int:kb_id>/chat-stream", views.ChatStreamView.as_view(), name="rag-chat-stream"),
]
