"""LLM 服务封装：DeepSeek Chat API + 通义千问 Embedding + 多模态"""
import json
import logging
import os
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
    """DeepSeek Chat + DashScope Embedding"""

    _client = None

    @classmethod
    def _get_client(cls) -> OpenAI:
        if cls._client is None:
            cls._client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
            )
        return cls._client

    @classmethod
    def generate_query_embedding(cls, text: str) -> list[float]:
        """单条文本向量化（用于问答检索）"""
        import dashscope
        from dashscope import TextEmbedding

        dashscope.api_key = settings.DASHSCOPE_API_KEY
        resp = TextEmbedding.call(
            model="text-embedding-v3",
            input=text,
            dimension=1024,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Embedding API 失败: {resp.code} - {resp.message}")
        return resp.output["embeddings"][0]["embedding"]

    @classmethod
    def chat(cls, question: str, context_chunks: list[dict]) -> dict:
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
            max_tokens=2000,
        )

        answer = response.choices[0].message.content or ""
        tokens_used = response.usage.total_tokens if response.usage else 0

        return {"answer": answer, "tokens_used": tokens_used}

    @classmethod
    def chat_stream(cls, question: str, context_chunks: list[dict]) -> Generator[str, None, None]:
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
            max_tokens=2000,
            stream=True,
        )

        for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield f"data: {json.dumps({'type': 'token', 'content': delta.content})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    @classmethod
    def multimodal_chat_stream(
        cls, question: str, context_chunks: list[dict], image_paths: list[str] | None = None,
    ) -> Generator[str, None, None]:
        import dashscope
        from dashscope import MultiModalConversation

        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            meta = chunk.get("metadata", {})
            file_name = meta.get("file_name", "未知文档")
            chunk_idx = meta.get("chunk_index", 0)
            context_parts.append(
                f"[来源{i}: {file_name}-块{chunk_idx}]\n{chunk['content']}"
            )
        context_text = "\n\n".join(context_parts) if context_parts else "（无相关参考资料）"

        MULTIMODAL_PROMPT = f"""你是一个专业的企业知识库助手。请根据以下提供的参考资料以及用户上传的图片来回答用户的问题。

规则：
1. 如果参考资料中包含答案，请基于参考资料回答，并在回答中标注来源（如 [来源: 文档名-块序号]）。
2. 如果参考资料中没有足够信息，请结合图片内容进行回答。
3. 不要编造不在参考资料或图片中的信息。
4. 回答要准确、简洁、有条理。

参考资料：
{context_text}"""

        user_content: list[dict] = [{"text": question}]
        if image_paths:
            for img_path in image_paths:
                try:
                    abs_path = os.path.abspath(img_path)
                    user_content.append({"image": f"file://{abs_path}"})
                except Exception as e:
                    logger.warning("添加图片失败 %s: %s", img_path, e)

        messages = [
            {"role": "system", "content": [{"text": MULTIMODAL_PROMPT}]},
            {"role": "user", "content": user_content},
        ]

        dashscope.api_key = settings.DASHSCOPE_API_KEY
        model = settings.DASHSCOPE_CHAT_MODEL

        responses = MultiModalConversation.call(
            model=model,
            messages=messages,
            stream=True,
        )

        prev_text = ""
        for chunk in responses:
            if chunk.output and chunk.output.get("choices"):
                choice = chunk.output["choices"][0]
                if choice.get("message") and choice["message"].get("content"):
                    for item in choice["message"]["content"]:
                        if item.get("text"):
                            cur = item["text"]
                            delta = cur[len(prev_text):]
                            if delta:
                                yield f"data: {json.dumps({'type': 'token', 'content': delta})}\n\n"
                            prev_text = cur

        yield f"data: {json.dumps({'type': 'done'})}\n\n"
