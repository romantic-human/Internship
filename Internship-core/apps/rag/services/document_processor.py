"""文档处理服务：文件解析 → 分块 → 向量化 → 存储"""
import os
import uuid
import logging

from django.conf import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from apps.rag.models import Document, DocumentChunk
from .vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理核心逻辑"""

    @staticmethod
    def parse_file(file_path: str, file_type: str) -> str:
        """解析文件为纯文本"""
        abs_path = os.path.join(settings.MEDIA_ROOT, file_path)

        if file_type in ("txt", "md"):
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        if file_type == "pdf":
            from pypdf import PdfReader
            reader = PdfReader(abs_path)
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)

        if file_type == "docx":
            from docx import Document as DocxDocument
            doc = DocxDocument(abs_path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

        raise ValueError(f"不支持的文件类型: {file_type}")

    @staticmethod
    def split_text(text: str) -> list[str]:
        """使用 RecursiveCharacterTextSplitter 分块"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""],
            length_function=len,
        )
        return [chunk for chunk in splitter.split_text(text) if chunk.strip()]

    @staticmethod
    def generate_embeddings(texts: list[str]) -> list[list[float]]:
        """调用通义千问 text-embedding-v3 批量向量化"""
        import dashscope
        from dashscope import TextEmbedding

        dashscope.api_key = settings.DASHSCOPE_API_KEY

        all_embeddings = []
        batch_size = 25  # DashScope 单次最多 25 条

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            resp = TextEmbedding.call(
                model="text-embedding-v3",
                input=batch,
                dimension=1024,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Embedding API 调用失败: {resp.code} - {resp.message}")
            for item in resp.output["embeddings"]:
                all_embeddings.append(item["embedding"])

        return all_embeddings

    @classmethod
    def process_document(cls, document_id: int):
        """完整处理流程：解析 → 分块 → 向量化 → 存储"""
        doc = Document.objects.get(id=document_id)
        try:
            doc.status = Document.Status.PROCESSING
            doc.save(update_fields=["status", "update_time"])

            # 1. 解析文件
            text = cls.parse_file(doc.file_path, doc.file_type)
            if not text.strip():
                raise ValueError("文件内容为空")

            # 2. 分块
            chunks = cls.split_text(text)
            if not chunks:
                raise ValueError("分块结果为空")

            # 3. 向量化
            embeddings = cls.generate_embeddings(chunks)

            # 4. 创建 DocumentChunk 记录 + 存入 ChromaDB
            ids = []
            documents = []
            emb_list = []
            metadatas = []

            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = uuid.uuid4().hex
                DocumentChunk.objects.create(
                    document=doc,
                    chunk_index=idx,
                    content=chunk_text,
                    vector_id=vector_id,
                    token_count=len(chunk_text),
                )
                ids.append(vector_id)
                documents.append(chunk_text)
                emb_list.append(embedding)
                metadatas.append({
                    "doc_id": doc.id,
                    "chunk_index": idx,
                    "file_name": doc.file_name,
                })

            # 5. 批量写入 ChromaDB
            VectorStoreService.add_chunks(
                kb_id=doc.knowledge_base_id,
                ids=ids,
                documents=documents,
                embeddings=emb_list,
                metadatas=metadatas,
            )

            # 6. 更新统计
            doc.chunk_count = len(chunks)
            doc.status = Document.Status.COMPLETED
            doc.save(update_fields=["chunk_count", "status", "update_time"])

            # 更新知识库统计
            kb = doc.knowledge_base
            kb.doc_count = kb.documents.filter(status=Document.Status.COMPLETED).count()
            kb.chunk_count = DocumentChunk.objects.filter(
                document__knowledge_base=kb
            ).count()
            kb.save(update_fields=["doc_count", "chunk_count", "update_time"])

            logger.info(f"文档处理完成: {doc.file_name}, {len(chunks)} 块")

        except Exception as e:
            logger.exception(f"文档处理失败: {doc.file_name}")
            doc.status = Document.Status.FAILED
            doc.error_message = str(e)
            doc.save(update_fields=["status", "error_message", "update_time"])
        finally:
            # 清理线程中的数据库连接
            from django.db import connections
            connections.close_all()
