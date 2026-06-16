"""LLM 服务封装：DeepSeek Chat API + 通义千问 Embedding + 多模态"""
import base64
import json
import logging
from typing import Generator
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个专业的企业知识库助手。请根据以下提供的参考资料来回答用户的问题。

规则：
1. 如果参考资料中包含答案，请基于参考资料回答，并在回答中标注来源（如 [来源: 文档名-块序号]）。
2. 如果参考资料中没有足够信息，请明确告知用户"根据现有知识库未找到相关信息"。
3. 不要编造不在参考资料中的信息。
4. 回答要准确、简洁、有条理。

参考资料：
{context}"""


class LLMService:
    """DeepSeek Chat + DashScope Embedding + 多模态"""

    _client = None
    _multimodal_client = None  # 多模态专用 client

    @classmethod
    def _get_client(cls) -> OpenAI:
        if cls._client is None:
            cls._client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
            )
        return cls._client

    @classmethod
    def _get_multimodal_client(cls) -> OpenAI:
        """获取多模态专用 client（使用智谱 API）"""
        if cls._multimodal_client is None:
            cls._multimodal_client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
            )
        return cls._multimodal_client

    @classmethod
    def generate_query_embedding(cls, text: str) -> list[float]:
        """单条文本向量化（用于问答检索）- 使用智谱免费 embedding-3 模型"""
        client = cls._get_client()
        resp = client.embeddings.create(
            model="embedding-3",
            input=text,
        )
        return resp.data[0].embedding

    @classmethod
    def chat(cls, question: str, context_chunks: list[dict]) -> dict:
        """
        问答：构建 Prompt → 调用 DeepSeek Chat API

        Args:
            question: 用户问题
            context_chunks: [{"content": "...", "metadata": {"file_name": "...", "chunk_index": 0}}, ...]

        Returns:
            {"answer": "...", "tokens_used": 123}
        """
        # 拼接参考资料
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            meta = chunk.get("metadata", {})
            file_name = meta.get("file_name", "未知文档")
            chunk_idx = meta.get("chunk_index", 0)
            context_parts.append(
                f"[来源{i}: {file_name}-块{chunk_idx}]\n{chunk['content']}"
            )
        context_text = "\n\n".join(context_parts) if context_parts else "（无相关参考资料）"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context_text)},
            {"role": "user", "content": question},
        ]

        client = cls._get_client()
        response = client.chat.completions.create(
            model=settings.DEEPSEEK_CHAT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )

        answer = response.choices[0].message.content or ""
        tokens_used = response.usage.total_tokens if response.usage else 0

        return {
            "answer": answer,
            "tokens_used": tokens_used,
        }

    @classmethod
    def chat_stream(cls, question: str, context_chunks: list[dict]) -> Generator[str, None, None]:
        """
        流式问答：逐 token 产出 SSE 格式的 JSON 字符串
        Yields: SSE data lines with type "token"
        """
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            meta = chunk.get("metadata", {})
            file_name = meta.get("file_name", "未知文档")
            chunk_idx = meta.get("chunk_index", 0)
            context_parts.append(
                f"[来源{i}: {file_name}-块{chunk_idx}]\n{chunk['content']}"
            )
        context_text = "\n\n".join(context_parts) if context_parts else "（无相关参考资料）"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context_text)},
            {"role": "user", "content": question},
        ]

        client = cls._get_client()
        response = client.chat.completions.create(
            model=settings.DEEPSEEK_CHAT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
            stream=True,
        )

        for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield f"data: {json.dumps({'type': 'token', 'content': delta.content})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    # ── 多模态问答（图片 + 文本）──────────────────────────────

    @classmethod
    def _build_context_text(cls, context_chunks: list[dict]) -> str:
        """拼接参考资料文本（复用于 chat / chat_with_image）"""
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            meta = chunk.get("metadata", {})
            file_name = meta.get("file_name", "未知文档")
            chunk_idx = meta.get("chunk_index", 0)
            context_parts.append(
                f"[来源{i}: {file_name}-块{chunk_idx}]\n{chunk['content']}"
            )
        return "\n\n".join(context_parts) if context_parts else "（无相关参考资料）"

    @classmethod
    def chat_with_image(cls, question: str, image_base64: str, context_chunks: list[dict]) -> dict:
        """
        图文多模态问答：支持图片+文本输入

        Args:
            question: 用户问题
            image_base64: 图片的 base64 编码字符串
            context_chunks: RAG 检索到的参考资料

        Returns:
            {"answer": "...", "tokens_used": 123}
        """
        context_text = cls._build_context_text(context_chunks)

        user_content = []
        # 添加图片
        if image_base64:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_base64}"},
            })
        # 添加文本问题
        user_content.append({"type": "text", "text": question})

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context_text)},
            {"role": "user", "content": user_content},
        ]

        client = cls._get_multimodal_client()  # 使用多模态专用 client
        multimodal_model = getattr(settings, "MULTIMODAL_MODEL", "qwen-vl-plus")
        response = client.chat.completions.create(
            model=multimodal_model,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )

        answer = response.choices[0].message.content or ""
        tokens_used = response.usage.total_tokens if response.usage else 0

        return {
            "answer": answer,
            "tokens_used": tokens_used,
        }

    @classmethod
    def chat_with_image_stream(cls, question: str, image_base64: str, context_chunks: list[dict]) -> Generator[str, None, None]:
        """
        图文多模态流式问答：支持图片+文本输入

        Yields: SSE data lines with type "token"
        """
        context_text = cls._build_context_text(context_chunks)

        user_content = []
        if image_base64:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_base64}"},
            })
        user_content.append({"type": "text", "text": question})

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context_text)},
            {"role": "user", "content": user_content},
        ]

        client = cls._get_multimodal_client()  # 使用多模态专用 client
        multimodal_model = getattr(settings, "MULTIMODAL_MODEL", "qwen-vl-plus")
        response = client.chat.completions.create(
            model=multimodal_model,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
            stream=True,
        )

        for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield f"data: {json.dumps({'type': 'token', 'content': delta.content})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"
