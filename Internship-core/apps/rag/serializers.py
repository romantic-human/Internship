"""RAG 知识库模块序列化器"""
from rest_framework import serializers
from .models import KnowledgeBase, Document, DocumentChunk


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source="creator.username", read_only=True, default="")

    class Meta:
        model = KnowledgeBase
        fields = [
            "id", "name", "description", "status",
            "doc_count", "chunk_count",
            "creator", "creator_name",
            "create_time", "update_time",
        ]
        read_only_fields = ["id", "doc_count", "chunk_count", "creator", "create_time", "update_time"]


class DocumentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id", "knowledge_base", "file_name", "file_type",
            "file_size", "chunk_count", "status", "status_display",
            "error_message", "create_time", "update_time",
        ]
        read_only_fields = ["id", "chunk_count", "status", "error_message", "create_time", "update_time"]


class DocumentChunkSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source="document.file_name", read_only=True)

    class Meta:
        model = DocumentChunk
        fields = [
            "id", "document", "document_name",
            "chunk_index", "content", "token_count",
            "create_time",
        ]


class ChatRequestSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, max_length=2000)
    image = serializers.CharField(required=False, allow_blank=True, default="")


class ChatSourceSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    document_name = serializers.CharField()
    chunk_index = serializers.IntegerField()
    content = serializers.CharField()
    relevance_score = serializers.FloatField()


class ChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    sources = ChatSourceSerializer(many=True)
    tokens_used = serializers.IntegerField()
