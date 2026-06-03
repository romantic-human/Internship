"""权限模块 — 参考《组织架构模块设计方案.md》第 5.5 节"""
from django.db import models


class Permission(models.Model):
    """权限表 — 对应设计文档 3.3.6"""

    permission_name = models.CharField(max_length=64, verbose_name="权限名称")
    permission_key = models.CharField(max_length=64, unique=True, verbose_name="权限标识")
    sort_order = models.IntegerField(default=0, verbose_name="排序号")
    status = models.SmallIntegerField(default=1, verbose_name="状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "sys_permission"
        verbose_name = "权限"
        verbose_name_plural = verbose_name
        ordering = ["sort_order"]


class MenuPermissionRelation(models.Model):
    """菜单-权限关联表 — 对应设计文档 3.3.7"""

    menu = models.ForeignKey("menu.Menu", on_delete=models.CASCADE, verbose_name="菜单")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name="权限")

    class Meta:
        db_table = "sys_menu_permission_relation"
        unique_together = ("menu", "permission")