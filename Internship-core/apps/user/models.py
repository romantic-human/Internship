"""用户模块 — 参考《组织架构模块设计方案.md》第 5.2 节"""
import bcrypt
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """自定义用户管理器"""

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("用户名不能为空")
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", 1)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser):
    """用户表 — 对应设计文档 3.3.1 sys_user"""

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    objects = UserManager()

    username = models.CharField(max_length=64, unique=True, verbose_name="用户名")
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

    def set_password(self, raw_password: str):
        """使用 bcrypt 加密密码"""
        self.password = bcrypt.hashpw(
            raw_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        """验证密码"""
        if not self.password:
            return False
        return bcrypt.checkpw(
            raw_password.encode("utf-8"), self.password.encode("utf-8")
        )

    @property
    def is_active(self) -> bool:
        """Django 要求 — status=1 且未删除视为激活"""
        return self.status == 1

    @property
    def is_staff(self) -> bool:
        """Django Admin 权限"""
        return self.is_superuser

    @property
    def role_list(self) -> list:
        """获取用户角色标识列表"""
        relations = self.userrolerelation_set.select_related("role").all()
        return [r.role.role_key for r in relations if r.role.status == 1]

    @property
    def permission_list(self) -> list:
        """获取用户权限标识列表（通过角色-菜单关联获取）"""
        if self.is_superuser:
            return ["*:*:*"]
        # 通过 prefetch_related 优化查询
        role_ids = self.userrolerelation_set.values_list("role_id", flat=True)
        from apps.role.models import RoleMenuRelation
        from apps.permission.models import MenuPermissionRelation
        from apps.menu.models import Menu
        menu_ids = RoleMenuRelation.objects.filter(
            role_id__in=role_ids, role__status=1
        ).values_list("menu_id", flat=True)
        perm_ids = MenuPermissionRelation.objects.filter(
            menu_id__in=menu_ids
        ).values_list("permission_id", flat=True)
        from apps.permission.models import Permission
        perms = Permission.objects.filter(id__in=perm_ids, status=1).values_list(
            "permission_key", flat=True
        )
        return list(perms)

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class UserRoleRelation(models.Model):
    """用户-角色关联表 — 对应设计文档 3.3.3"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    role = models.ForeignKey("role.Role", on_delete=models.CASCADE, verbose_name="角色")

    class Meta:
        db_table = "sys_user_role_relation"
        unique_together = ("user", "role")