"""系统配置模块 — 参考《组织架构模块设计方案.md》第 5.8 节"""
from django.db import models


class SystemConfig(models.Model):
    """系统配置表 — 对应设计文档 3.3.10"""

    config_name = models.CharField(max_length=64, verbose_name="配置名称")
    config_key = models.CharField(max_length=64, unique=True, verbose_name="配置键")
    config_value = models.TextField(verbose_name="配置值")
    config_type = models.SmallIntegerField(default=0, verbose_name="配置类型")
    remark = models.CharField(max_length=255, blank=True, default="", verbose_name="备注")
    status = models.SmallIntegerField(default=1, verbose_name="状态")
    sort_order = models.IntegerField(default=0, verbose_name="排序号")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "sys_config"
        verbose_name = "系统配置"
        verbose_name_plural = verbose_name
        ordering = ["sort_order"]


class AIModelConfig(models.Model):
    """AI 模型配置表 — 支持多模型切换"""

    PROVIDER_CHOICES = [
        ("zhipu", "智谱 AI"),
        ("dashscope", "阿里云百炼"),
        ("openai", "OpenAI"),
        ("deepseek", "DeepSeek"),
        ("other", "其他"),
    ]

    MODEL_TYPE_CHOICES = [
        ("chat", "对话模型"),
        ("embedding", "向量模型"),
        ("multimodal", "多模态模型"),
    ]

    name = models.CharField("配置名称", max_length=100, help_text="如：智谱GLM-4-Flash")
    provider = models.CharField("提供商", max_length=50, choices=PROVIDER_CHOICES, default="zhipu")
    model_type = models.CharField("模型类型", max_length=20, choices=MODEL_TYPE_CHOICES)
    model_name = models.CharField("模型名称", max_length=100, help_text="如：glm-4-flash")
    api_key = models.CharField("API Key", max_length=500)
    api_base_url = models.CharField("API 地址", max_length=500, help_text="如：https://open.bigmodel.cn/api/paas/v4")
    is_default = models.BooleanField("是否默认", default=False)
    status = models.SmallIntegerField("状态", default=1, choices=[(1, "启用"), (0, "禁用")])
    remark = models.CharField("备注", max_length=255, blank=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "ai_model_config"
        verbose_name = "AI 模型配置"
        verbose_name_plural = verbose_name
        ordering = ["-is_default", "-create_time"]

    def __str__(self):
        return f"{self.name} ({self.get_model_type_display()})"