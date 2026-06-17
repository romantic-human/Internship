from django.conf import settings
from django.db import models
from utils.crypto import encrypt_password, decrypt_password


class DataSource(models.Model):
    name = models.CharField("数据源名称", max_length=100)
    db_type = models.CharField("数据库类型", max_length=20, default="mysql")
    host = models.CharField("主机地址", max_length=200, default="127.0.0.1")
    port = models.IntegerField("端口", default=3306)
    db_name = models.CharField("数据库名", max_length=100)
    username = models.CharField("用户名", max_length=100, default="root")
    password_enc = models.CharField("密码(加密)", max_length=500, blank=True, default="")
    description = models.TextField("描述", blank=True, default="")
    status = models.SmallIntegerField("状态", default=1, choices=[(1, "启用"), (0, "禁用")])
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="创建者",
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "nl2sql_datasource"
        ordering = ["-created_at"]
        verbose_name = "数据源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name} ({self.db_type}://{self.host}:{self.port}/{self.db_name})"

    def set_password(self, raw_password: str):
        """加密并保存密码"""
        self.password_enc = encrypt_password(raw_password) if raw_password else ""

    def get_password(self) -> str:
        """解密并返回密码明文"""
        return decrypt_password(self.password_enc)


class QueryHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name="查询用户",
    )
    datasource = models.ForeignKey(
        DataSource, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="数据源",
    )
    question = models.TextField("自然语言问题")
    generated_sql = models.TextField("生成的 SQL", blank=True, default="")
    execution_time = models.FloatField("执行耗时(秒)", default=0)
    result_count = models.IntegerField("结果行数", default=0)
    status = models.SmallIntegerField("状态", default=1, choices=[(0, "失败"), (1, "成功")])
    is_favorite = models.SmallIntegerField("是否收藏", default=0, choices=[(0, "否"), (1, "是")])
    error_message = models.TextField("错误信息", blank=True, default="")
    natural_language_result = models.TextField("自然语言解释", blank=True, default="")
    created_at = models.DateTimeField("查询时间", auto_now_add=True)

    class Meta:
        db_table = "nl2sql_query_history"
        ordering = ["-created_at"]
        verbose_name = "查询历史"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"[{self.user_id}] {self.question[:50]}"
