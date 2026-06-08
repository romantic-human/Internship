"""菜单模块 — 参考《组织架构模块设计方案.md》第 5.4 节"""
from django.db import models


class Menu(models.Model):
    """菜单表 — 对应设计文档 3.3.4"""

    def __str__(self):
        return self.menu_name

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="父菜单",
    )
    menu_name = models.CharField(max_length=64, verbose_name="菜单名称")
    menu_type = models.SmallIntegerField(default=0, verbose_name="菜单类型")
    path = models.CharField(max_length=255, blank=True, default="", verbose_name="路由路径")
    component = models.CharField(max_length=255, blank=True, default="", verbose_name="组件路径")
    icon = models.CharField(max_length=64, blank=True, default="", verbose_name="图标")
    permission = models.CharField(max_length=64, blank=True, default="", verbose_name="权限标识")
    sort_order = models.IntegerField(default=0, verbose_name="排序号")
    visible = models.SmallIntegerField(default=1, verbose_name="是否可见")
    is_frame = models.SmallIntegerField(default=0, verbose_name="是否外链")
    status = models.SmallIntegerField(default=1, verbose_name="状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "sys_menu"
        verbose_name = "菜单"
        verbose_name_plural = verbose_name
        ordering = ["sort_order"]