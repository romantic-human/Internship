"""用户模块 — 参考《组织架构模块设计方案.md》第 5.2 节"""
from django.db import models


class User(models.Model):
    """用户表 — 对应设计文档 3.3.1 sys_user"""

    username = models.CharField(max_length=64, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=128, verbose_name="密码")
    nickname = models.CharField(max_length=64, blank=True, default="", verbose_name="昵称")
    real_name = models.CharField(max_length=64, blank=True, default="", verbose_name="真实姓名")
    email = models.EmailField(max_length=128, blank=True, default="", verbose_name="邮箱")
    telephone = models.CharField(max_length=20, blank=True, default="", verbose_name="手机号")
    gender = models.SmallIntegerField(default=0, verbose_name="性别")
    avatar = models.CharField(max_length=255, blank=True, default="", verbose_name="头像")
    department = models.ForeignKey(
        "department.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="所属部门",
    )
    status = models.SmallIntegerField(default=1, verbose_name="状态")
    is_superuser = models.BooleanField(default=False, verbose_name="超级管理员")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="最后登录时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "sys_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]

    def __str__(self):
        return self.username


class UserRoleRelation(models.Model):
    """用户-角色关联表 — 对应设计文档 3.3.3"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    role = models.ForeignKey("role.Role", on_delete=models.CASCADE, verbose_name="角色")

    class Meta:
        db_table = "sys_user_role_relation"
        unique_together = ("user", "role")
