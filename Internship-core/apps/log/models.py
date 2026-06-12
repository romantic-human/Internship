"""日志模块 — 参考《组织架构模块设计方案.md》第 5.7 节"""
from django.db import models


class OperationLog(models.Model):
    """操作日志表 — 对应设计文档 3.3.9"""

    username = models.CharField(max_length=64, verbose_name="操作用户")
    module = models.CharField(max_length=64, verbose_name="操作模块")
    operation = models.CharField(max_length=64, verbose_name="操作类型")
    method = models.CharField(max_length=10, verbose_name="请求方法")
    request_url = models.CharField(max_length=255, verbose_name="请求URL")
    request_params = models.TextField(blank=True, default="", verbose_name="请求参数")
    response_result = models.TextField(blank=True, default="", verbose_name="响应结果")
    ip = models.CharField(max_length=64, blank=True, default="", verbose_name="操作IP")
    status = models.SmallIntegerField(default=1, verbose_name="操作状态")
    execution_time = models.IntegerField(default=0, verbose_name="执行耗时(ms)")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")

    class Meta:
        db_table = "sys_operation_log"
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]