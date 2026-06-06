"""角色模块 — 参考《组织架构模块设计方案.md》第 5.3 节"""
from django.db import models


class Role(models.Model):
    """角色表 — 对应设计文档 3.3.2"""

    def __str__(self):
        return self.role_name

    role_name = models.CharField(max_length=64, unique=True, verbose_name="角色名称")
    role_key = models.CharField(max_length=64, unique=True, verbose_name="角色标识")
    role_sort = models.IntegerField(default=0, verbose_name="排序号")
    status = models.SmallIntegerField(default=1, verbose_name="状态")
    remark = models.CharField(max_length=255, blank=True, default="", verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "sys_role"
        verbose_name = "角色"
        verbose_name_plural = verbose_name
        ordering = ["role_sort"]


class RoleMenuRelation(models.Model):
    """角色-菜单关联表 — 对应设计文档 3.3.5"""

    def __str__(self):
        return f"{self.role} - {self.menu}"

    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="角色")
    menu = models.ForeignKey("menu.Menu", on_delete=models.CASCADE, verbose_name="菜单")

    class Meta:
        db_table = "sys_role_menu_relation"
        unique_together = ("role", "menu")
        verbose_name = "角色-菜单关联"
        verbose_name_plural = verbose_name