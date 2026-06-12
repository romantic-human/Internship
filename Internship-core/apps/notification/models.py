"""消息通知模块"""
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """系统通知"""

    TYPE_CHOICES = [
        (0, "系统通知"),
        (1, "待办事项"),
        (2, "提醒"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="接收用户",
    )
    title = models.CharField(max_length=128, verbose_name="标题")
    content = models.TextField(blank=True, default="", verbose_name="内容")
    notification_type = models.SmallIntegerField(
        choices=TYPE_CHOICES, default=0, verbose_name="通知类型",
    )
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    extra_data = models.JSONField(null=True, blank=True, verbose_name="附加数据")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    read_time = models.DateTimeField(null=True, blank=True, verbose_name="已读时间")

    class Meta:
        db_table = "sys_notification"
        verbose_name = "系统通知"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"
