"""数据库连接服务：连接外部数据库，获取表结构元数据"""
import logging
import pymysql
from django.db import connection

logger = logging.getLogger(__name__)


def get_tables_and_columns(db_type: str, host: str, port: int, db_name: str,
                            username: str, password: str) -> dict:
    """
    连接外部数据库，获取所有表名及字段信息

    Returns:
        {"tables": [{
            "table_name": "...",
            "table_comment": "...",
            "columns": [{"name": "...", "type": "...", "nullable": bool, "comment": "..."}, ...]
        }, ...]}
    """
    conn = pymysql.connect(
        host=host,
        port=port,
        user=username,
        password=password,
        database=db_name,
        charset="utf8mb4",
        connect_timeout=10,
    )
    result = {"tables": []}
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT TABLE_NAME, TABLE_COMMENT
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME
            """, (db_name,))
            tables = cursor.fetchall()

            for (table_name, table_comment) in tables:
                cursor.execute("""
                    SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_COMMENT, COLUMN_KEY
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION
                """, (db_name, table_name))
                columns = []
                for (col_name, col_type, nullable, col_comment, col_key) in cursor.fetchall():
                    columns.append({
                        "name": col_name,
                        "type": col_type,
                        "nullable": nullable == "YES",
                        "comment": col_comment or "",
                        "is_primary": col_key == "PRI",
                    })
                result["tables"].append({
                    "table_name": table_name,
                    "table_comment": table_comment or "",
                    "columns": columns,
                })
    finally:
        conn.close()
    return result


def build_schema_ddl(tables_meta: dict) -> str:
    """
    将表结构元数据转换为 DDL 描述字符串（LLM Prompt 用）

    Example output:
        CREATE TABLE `sys_user` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
          `username` varchar(64) NOT NULL COMMENT '用户名',
          ...
        ) COMMENT='用户表';
    """
    parts = []
    for t in tables_meta.get("tables", []):
        lines = [f"CREATE TABLE `{t['table_name']}` ("]
        col_lines = []
        for c in t["columns"]:
            nullable_str = "NOT NULL" if not c["nullable"] else "DEFAULT NULL"
            comment_str = f" COMMENT '{c['comment']}'" if c["comment"] else ""
            pk_str = " AUTO_INCREMENT" if c.get("is_primary") else ""
            col_lines.append(f"  `{c['name']}` {c['type']} {nullable_str}{pk_str}{comment_str}")
        lines.append(",\n".join(col_lines))
        comment = f" COMMENT='{t['table_comment']}'" if t["table_comment"] else ""
        lines.append(f"){comment};")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def test_connection(db_type: str, host: str, port: int, db_name: str,
                    username: str, password: str) -> tuple[bool, str]:
    """测试数据库连接是否成功"""
    try:
        conn = pymysql.connect(
            host=host, port=port, user=username,
            password=password, database=db_name,
            charset="utf8mb4", connect_timeout=10,
        )
        conn.close()
        return True, "连接成功"
    except Exception as e:
        return False, str(e)
