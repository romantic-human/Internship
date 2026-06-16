"""RAG 知识库模块视图"""
import json
import os
import threading
import logging

from django.conf import settings
from django.db import close_old_connections
from django.http import StreamingHttpResponse
from rest_framework import viewsets, status as http_status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

from utils.response import APIResponse
from utils.permissions import HasPermission
from .models import KnowledgeBase, Document, DocumentChunk
from .serializers import (
    KnowledgeBaseSerializer, DocumentSerializer, DocumentChunkSerializer,
    ChatRequestSerializer, MultimodalChatRequestSerializer,
)
from .services.vector_store import VectorStoreService
from .services.document_processor import DocumentProcessor
from .services.llm_service import LLMService

logger = logging.getLogger(__name__)


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    """知识库 CRUD"""
    queryset = KnowledgeBase.objects.select_related("creator").all()
    serializer_class = KnowledgeBaseSerializer
    permission_key = "rag:kb:list"
    permission_key_map = {
        "create": "rag:kb:add",
        "update": "rag:kb:edit",
        "destroy": "rag:kb:delete",
    }

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), HasPermission()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(creator=request.user)
        return APIResponse.success(data=serializer.data, message="创建成功")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        name = request.query_params.get("name", "").strip()
        if name:
            queryset = queryset.filter(name__icontains=name)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data={"records": serializer.data, "total": queryset.count()})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(data=serializer.data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        kb_id = instance.id
        try:
            VectorStoreService.delete_collection(kb_id)
        except Exception as e:
            logger.warning("ChromaDB cleanup failed for kb %s: %s", kb_id, e)
        for doc in instance.documents.only("file_path").iterator():
            abs_path = os.path.join(settings.MEDIA_ROOT, doc.file_path)
            try:
                if os.path.exists(abs_path):
                    os.remove(abs_path)
            except OSError as e:
                logger.warning("删除文件失败 %s: %s", abs_path, e)
        # ORM 级联删除
        instance.delete()
        return APIResponse.success(message="删除成功")


class DocumentViewSet(viewsets.GenericViewSet):
    """文档管理"""
    queryset = Document.objects.select_related("knowledge_base").all()
    serializer_class = DocumentSerializer
    permission_key = "rag:doc:list"
    permission_key_map = {
        "destroy": "rag:doc:delete",
        "upload": "rag:doc:upload",
        "reprocess": "rag:doc:upload",
    }

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), HasPermission()]

    def list(self, request, *args, **kwargs):
        kb_id = request.query_params.get("knowledge_base")
        queryset = self.get_queryset()
        if kb_id:
            try:
                kb_id_int = int(kb_id)
                queryset = queryset.filter(knowledge_base_id=kb_id_int)
            except (ValueError, TypeError):
                return APIResponse.error(message="无效的知识库ID", code=400, http_status=400)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data={"records": serializer.data, "total": queryset.count()})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        kb_id = instance.knowledge_base_id
        doc_id = instance.id
        try:
            VectorStoreService.delete_by_document(kb_id, doc_id)
        except Exception as e:
            logger.warning("ChromaDB cleanup failed for doc %s: %s", doc_id, e)
        abs_path = os.path.join(settings.MEDIA_ROOT, instance.file_path)
        if os.path.exists(abs_path):
            try:
                os.remove(abs_path)
            except OSError as e:
                logger.warning("File deletion failed %s: %s", abs_path, e)
        instance.delete()
        kb = instance.knowledge_base
        kb.doc_count = kb.documents.filter(status=Document.Status.COMPLETED).count()
        kb.chunk_count = DocumentChunk.objects.filter(document__knowledge_base=kb).count()
        kb.save(update_fields=["doc_count", "chunk_count", "update_time"])
        return APIResponse.success(message="删除成功")

    @action(detail=False, methods=["post"], url_path="upload", parser_classes=[MultiPartParser])
    def upload(self, request):
        kb_id = request.data.get("knowledge_base_id")
        if not kb_id:
            return APIResponse.error(message="缺少 knowledge_base_id", code=2000, http_status=400)
        try:
            kb = KnowledgeBase.objects.get(id=kb_id, status=1)
        except KnowledgeBase.DoesNotExist:
            return APIResponse.error(message="知识库不存在或已禁用", code=2004, http_status=404)

        file = request.FILES.get("file")
        if not file:
            return APIResponse.error(message="请选择文件", code=2000, http_status=400)

        # 校验文件类型
        ext = os.path.splitext(file.name)[1].lower().lstrip(".")
        allowed = ("pdf", "txt", "md", "docx")
        if ext not in allowed:
            return APIResponse.error(
                message=f"不支持的格式，仅支持: {', '.join(allowed)}",
                code=2000, http_status=400,
            )

        # 校验文件大小
        max_size = settings.RAG_MAX_FILE_SIZE_MB * 1024 * 1024
        if file.size > max_size:
            return APIResponse.error(
                message=f"文件大小超过限制 ({settings.RAG_MAX_FILE_SIZE_MB}MB)",
                code=2000, http_status=400,
            )

        # 保存文件
        upload_dir = os.path.join(settings.MEDIA_ROOT, "rag_docs", str(kb_id))
        os.makedirs(upload_dir, exist_ok=True)
        safe_name = os.path.basename(file.name).replace("/", "_").replace("\\", "_")
        filename = f"{os.urandom(8).hex()}_{safe_name}"
        file_path = os.path.join("rag_docs", str(kb_id), filename)
        abs_path = os.path.join(settings.MEDIA_ROOT, file_path)
        with open(abs_path, "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)

        # 创建 Document 记录
        doc = Document.objects.create(
            knowledge_base=kb,
            file_name=file.name,
            file_path=file_path,
            file_type=ext,
            file_size=file.size,
            status=Document.Status.PENDING,
        )

        # 后台线程处理
        close_old_connections()
        threading.Thread(
            target=DocumentProcessor.process_document,
            args=(doc.id,),
            daemon=True,
        ).start()

        serializer = self.get_serializer(doc)
        return APIResponse.success(data=serializer.data, message="上传成功，正在处理")

    @action(detail=True, methods=["post"], url_path="reprocess")
    def reprocess(self, request, pk=None):
        doc = self.get_object()
        if doc.status != Document.Status.FAILED:
            return APIResponse.error(message="只能重新处理失败的文档", code=2000, http_status=400)
        # 清理旧数据（ChromDB + ORM）
        VectorStoreService.delete_by_document(doc.knowledge_base_id, doc.id)
        DocumentChunk.objects.filter(document=doc).delete()
        doc.status = Document.Status.PENDING
        doc.error_message = ""
        doc.save(update_fields=["status", "error_message", "update_time"])
        close_old_connections()
        threading.Thread(
            target=DocumentProcessor.process_document,
            args=(doc.id,),
            daemon=True,
        ).start()
        serializer = self.get_serializer(doc)
        return APIResponse.success(data=serializer.data, message="正在重新处理")


class ChatView(APIView):
    """RAG 问答接口"""
    permission_classes = [IsAuthenticated, HasPermission]
    permission_key = "rag:chat"

    def post(self, request, kb_id):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data["question"]

        # 验证知识库
        try:
            kb = KnowledgeBase.objects.get(id=kb_id, status=1)
        except KnowledgeBase.DoesNotExist:
            return APIResponse.error(message="知识库不存在或已禁用", code=2004, http_status=404)

        try:
            # 1. 向量化问题
            query_embedding = LLMService.generate_query_embedding(question)

            # 2. ChromaDB 检索
            results = VectorStoreService.search(
                kb_id=kb_id,
                query_embedding=query_embedding,
                top_k=settings.RAG_TOP_K,
            )

            if not results:
                return APIResponse.success(data={
                    "answer": "根据现有知识库未找到相关信息。",
                    "sources": [],
                    "tokens_used": 0,
                })

            # 3. 构建来源信息
            sources = []
            for r in results:
                meta = r.get("metadata", {})
                # distance → relevance_score (cosine distance → similarity)
                relevance = max(0, 1 - r.get("distance", 0))
                sources.append({
                    "document_id": meta.get("doc_id", 0),
                    "document_name": meta.get("file_name", "未知"),
                    "chunk_index": meta.get("chunk_index", 0),
                    "content": r.get("content", "")[:200],
                    "relevance_score": round(relevance, 4),
                })

            # 4. 调用 LLM
            llm_result = LLMService.chat(question, results)

            return APIResponse.success(data={
                "answer": llm_result["answer"],
                "sources": sources,
                "tokens_used": llm_result["tokens_used"],
            })

        except Exception as e:
            logger.exception("问答处理失败")
            return APIResponse.error(message=f"问答处理失败: {str(e)}", code=5000, http_status=500)


class ChatStreamView(APIView):
    """RAG 流式问答接口（SSE）"""
    permission_classes = [IsAuthenticated, HasPermission]
    permission_key = "rag:chat"

    def post(self, request, kb_id):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data["question"]

        try:
            kb = KnowledgeBase.objects.get(id=kb_id, status=1)
        except KnowledgeBase.DoesNotExist:
            return APIResponse.error(message="知识库不存在或已禁用", code=2004, http_status=404)

        def event_stream():
            try:
                query_embedding = LLMService.generate_query_embedding(question)
                results = VectorStoreService.search(
                    kb_id=kb_id,
                    query_embedding=query_embedding,
                    top_k=settings.RAG_TOP_K,
                )

                if not results:
                    yield f"data: {json.dumps({'type': 'answer', 'content': '根据现有知识库未找到相关信息。'})}\n\n"
                    yield f"data: {json.dumps({'type': 'sources', 'content': []})}\n\n"
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return

                sources = []
                for r in results:
                    meta = r.get("metadata", {})
                    relevance = max(0, 1 - r.get("distance", 0))
                    sources.append({
                        "document_id": meta.get("doc_id", 0),
                        "document_name": meta.get("file_name", "未知"),
                        "chunk_index": meta.get("chunk_index", 0),
                        "content": r.get("content", "")[:200],
                        "relevance_score": round(relevance, 4),
                    })

                for sse_data in LLMService.chat_stream(question, results):
                    yield sse_data

                yield f"data: {json.dumps({'type': 'sources', 'content': sources})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

            except Exception as e:
                logger.exception("流式问答处理失败")
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

        response = StreamingHttpResponse(
            streaming_content=event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


class ChatMultimodalView(APIView):
    """多模态 RAG 问答接口（SSE 流式，支持图文混合输入）"""
    permission_classes = [IsAuthenticated, HasPermission]
    permission_key = "rag:chat"
    parser_classes = [MultiPartParser]

    def post(self, request, kb_id):
        serializer = MultimodalChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data["question"]
        images = serializer.validated_data.get("images", [])

        try:
            kb = KnowledgeBase.objects.get(id=kb_id, status=1)
        except KnowledgeBase.DoesNotExist:
            return APIResponse.error(message="知识库不存在或已禁用", code=2004, http_status=404)

        def event_stream():
            image_paths: list[str] = []
            try:
                # 保存上传的图片到临时文件
                upload_dir = os.path.join(settings.MEDIA_ROOT, "temp_chat_images", str(kb_id))
                os.makedirs(upload_dir, exist_ok=True)
                for img in images:
                    ext = os.path.splitext(img.name)[1].lower()
                    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                        continue
                    safe_name = f"{os.urandom(8).hex()}{ext}"
                    abs_path = os.path.join(upload_dir, safe_name)
                    with open(abs_path, "wb") as f:
                        for chunk in img.chunks():
                            f.write(chunk)
                    image_paths.append(abs_path)

                # 向量检索
                query_embedding = LLMService.generate_query_embedding(question)
                results = VectorStoreService.search(
                    kb_id=kb_id,
                    query_embedding=query_embedding,
                    top_k=settings.RAG_TOP_K,
                )

                if not results and not image_paths:
                    yield f"data: {json.dumps({'type': 'answer', 'content': '根据现有知识库未找到相关信息。'})}\n\n"
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return

                sources = []
                for r in (results or []):
                    meta = r.get("metadata", {})
                    relevance = max(0, 1 - r.get("distance", 0))
                    sources.append({
                        "document_id": meta.get("doc_id", 0),
                        "document_name": meta.get("file_name", "未知"),
                        "chunk_index": meta.get("chunk_index", 0),
                        "content": r.get("content", "")[:200],
                        "relevance_score": round(relevance, 4),
                    })

                # 多模态 LLM 调用
                for sse_data in LLMService.multimodal_chat_stream(question, results or [], image_paths):
                    yield sse_data

                yield f"data: {json.dumps({'type': 'sources', 'content': sources})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

            except Exception as e:
                logger.exception("多模态问答处理失败")
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            finally:
                # 清理临时图片
                for p in image_paths:
                    try:
                        if os.path.exists(p):
                            os.remove(p)
                    except OSError:
                        pass

        response = StreamingHttpResponse(
            streaming_content=event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
