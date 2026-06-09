"""RAG 知识库模块数据模型"""
from django.db import models
from django.conf import settings


class KnowledgeBase(models.Model):
    """知识库"""
    name = models.CharField("名称", max_length=128)
    description = models.TextField("描述", blank=True, default="")
    status = models.SmallIntegerField("状态", default=1, choices=[(1, "启用"), (0, "禁用")])
    doc_count = models.IntegerField("文档总数", default=0)
    chunk_count = models.IntegerField("文档块总数", default=0)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="创建者",
    )
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "rag_knowledge_base"
        ordering = ["-create_time"]
        verbose_name = "知识库"

    def __str__(self):
        return self.name


class Document(models.Model):
    """文档"""

    class Status(models.IntegerChoices):
        PENDING = 0, "待处理"
        PROCESSING = 1, "处理中"
        COMPLETED = 2, "已完成"
        FAILED = 3, "失败"

    knowledge_base = models.ForeignKey(
        KnowledgeBase, on_delete=models.CASCADE,
        related_name="documents", verbose_name="所属知识库",
    )
    file_name = models.CharField("文件名", max_length=255)
    file_path = models.CharField("存储路径", max_length=500)
    file_type = models.CharField("文件类型", max_length=16)
    file_size = models.BigIntegerField("文件大小(字节)", default=0)
    chunk_count = models.IntegerField("分块数", default=0)
    status = models.SmallIntegerField(
        "状态", default=0, choices=Status.choices,
    )
    error_message = models.TextField("错误信息", blank=True, default="")
    create_time = models.DateTimeField("上传时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "rag_document"
        ordering = ["-create_time"]
        verbose_name = "文档"

    def __str__(self):
        return self.file_name


class DocumentChunk(models.Model):
    """文档块"""
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE,
        related_name="chunks", verbose_name="所属文档",
    )
    chunk_index = models.IntegerField("块序号")
    content = models.TextField("内容")
    vector_id = models.CharField("向量ID", max_length=64, unique=True)
    token_count = models.IntegerField("Token数", default=0)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "rag_document_chunk"
        ordering = ["document", "chunk_index"]
        verbose_name = "文档块"

    def __str__(self):
        return f"{self.document.file_name}#{self.chunk_index}"
