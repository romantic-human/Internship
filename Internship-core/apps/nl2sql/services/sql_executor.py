"""SQL 执行器：安全校验 + 执行 SQL + 返回结果"""
import logging
import re
import pymysql

logger = logging.getLogger(__name__)

FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "RENAME", "GRANT", "REVOKE", "EXECUTE",
    "CALL", "LOAD", "INTO OUTFILE", "INTO DUMPFILE",
]

SENSITIVE_COLUMNS = [
    "password", "password_enc", "token", "secret", "salt",
    "refresh_token", "access_token",
]

MAX_LIMIT = 1000
DEFAULT_LIMIT = 100
EXECUTION_TIMEOUT = 30


def validate_sql(sql: str) -> tuple[bool, str]:
    """校验 SQL 安全性：只允许 SELECT，禁止危险操作"""
    sql_upper = sql.strip().upper()

    if not sql_upper.startswith("SELECT"):
        return False, "只允许 SELECT 查询语句"

    for kw in FORBIDDEN_KEYWORDS:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, sql_upper):
            return False, f"SQL 中包含禁止的关键字: {kw}"



    for col in SENSITIVE_COLUMNS:
        if col.lower() in sql.lower():
            return False, f"SQL 中包含敏感字段: {col}"

    return True, ""


def ensure_limit(sql: str) -> str:
    """确保 SQL 包含 LIMIT 子句"""
    sql_stripped = sql.strip().rstrip(";")
    if re.search(r"\bLIMIT\s+\d+", sql_stripped, re.IGNORECASE):
        limit_match = re.search(r"\bLIMIT\s+(\d+)", sql_stripped, re.IGNORECASE)
        if limit_match:
            limit_val = int(limit_match.group(1))
            if limit_val > MAX_LIMIT:
                sql_stripped = re.sub(
                    r"\bLIMIT\s+\d+", f"LIMIT {MAX_LIMIT}", sql_stripped,
                    flags=re.IGNORECASE,
                )
        return sql_stripped + ";"
    return sql_stripped + f" LIMIT {DEFAULT_LIMIT};"


def execute_sql(host: str, port: int, db_name: str, username: str,
                password: str, sql: str) -> dict:
    """
    安全执行 SQL 查询并返回结果

    Returns:
        {"columns": ["col1", "col2", ...], "rows": [[val1, val2], ...], "row_count": N}
    """
    valid, msg = validate_sql(sql)
    if not valid:
        return {"error": msg}

    sql = ensure_limit(sql)

    conn = pymysql.connect(
        host=host, port=port, user=username,
        password=password, database=db_name,
        charset="utf8mb4", connect_timeout=10,
        cursorclass=pymysql.cursors.Cursor,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                row_count = len(rows)
                return {"columns": columns, "rows": rows, "row_count": row_count}
            return {"columns": [], "rows": [], "row_count": 0}
    finally:
        conn.close()
