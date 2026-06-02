"""部门模块 — 参考《组织架构模块设计方案.md》第 5.6 节"""
from django.db import models


class Department(models.Model):
    """部门表 — 对应设计文档 3.3.8"""

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="父部门",
    )
    dept_name = models.CharField(max_length=64, verbose_name="部门名称")
    leader = models.CharField(max_length=64, blank=True, default="", verbose_name="负责人")
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="联系电话")
    email = models.EmailField(max_length=128, blank=True, default="", verbose_name="邮箱")
    sort_order = models.IntegerField(default=0, verbose_name="排序号")
    status = models.SmallIntegerField(default=1, verbose_name="状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "sys_department"
        verbose_name = "部门"
        verbose_name_plural = verbose_name
        ordering = ["sort_order"]