"""NL2SQL 服务：将自然语言转换为 SQL"""
import json
import logging
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)

NL2SQL_SYSTEM_PROMPT = """你是一个专业的 SQL 生成助手。请根据用户提供的数据库表结构和自然语言问题，生成对应的 SQL 查询语句。

规则：
1. 只生成 SELECT 查询语句，不生成 INSERT/UPDATE/DELETE/DROP/ALTER 等语句。
2. 如果问题无法用 SELECT 查询回答，请说明原因。
3. 使用标准 SQL 语法，兼容 MySQL。
4. 默认添加 LIMIT 100，除非用户明确指定数量。
5. 列名和表名用反引号包裹。
6. 如果用户问"所有"或"全部"，仍添加 LIMIT 100 防止数据量过大。
7. 只返回 SQL 语句本身，不要添加额外解释。

数据库表结构：
{schema_ddl}

用户的自然语言问题是："""


class NL2SQLService:
    """NL2SQL 服务 — 调用 LLM 将自然语言转为 SQL"""

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
    def generate_sql(cls, schema_ddl: str, question: str) -> str:
        """将自然语言问题转为 SQL 语句"""
        prompt = NL2SQL_SYSTEM_PROMPT.format(schema_ddl=schema_ddl)
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ]
        client = cls._get_client()
        response = client.chat.completions.create(
            model=settings.DEEPSEEK_CHAT_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=1000,
        )
        sql = response.choices[0].message.content or ""
        sql = sql.strip()
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        return sql.strip()
