"""系统配置模块 — 参考《组织架构模块设计方案.md》第 5.8 节"""
from django.db import models


class SystemConfig(models.Model):
    """系统配置表 — 对应设计文档 3.3.10"""

    config_name = models.CharField(max_length=64, verbose_name="配置名称")
    config_key = models.CharField(max_length=64, unique=True, verbose_name="配置键")
    config_value = models.TextField(verbose_name="配置值")
    config_type = models.SmallIntegerField(default=0, verbose_name="配置类型")
    remark = models.CharField(max_length=255, blank=True, default="", verbose_name="备注")
    sort_order = models.IntegerField(default=0, verbose_name="排序号")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "sys_config"
        verbose_name = "系统配置"
        verbose_name_plural = verbose_name
        ordering = ["sort_order"]
