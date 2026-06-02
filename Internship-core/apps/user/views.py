"""用户模块视图 — 参考《组织架构模块设计方案.md》第 5.2 节"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from utils import APIResponse, HasPermission
from .models import User
from .serializers import (
    LoginSerializer,
    UserSerializer,
    UserListSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """用户管理 CRUD"""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        """用户登录 — POST /api/user/login"""
        # TODO: 实现 JWT 登录逻辑
        return APIResponse.success(data={"message": "待实现"})

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        """用户注册 — POST /api/user/register"""
        return APIResponse.success(data={"message": "待实现"})

    @action(detail=False, methods=["post"])
    def refresh_token(self, request):
        """刷新 Token — POST /api/user/refresh-token"""
        return APIResponse.success(data={"message": "待实现"})

    @action(detail=True, methods=["put"])
    def status(self, request, pk=None):
        """修改状态 — PUT /api/user/:id/status"""
        return APIResponse.success()

    @action(detail=False, methods=["put"])
    def reset_password(self, request):
        """重置密码 — PUT /api/user/reset-password"""
        return APIResponse.success()

    @action(detail=False, methods=["put"])
    def update_password(self, request):
        """修改自己的密码 — PUT /api/user/update-password"""
        return APIResponse.success()

    @action(detail=False, methods=["get"])
    def export(self, request):
        """导出用户 — GET /api/user/export"""
        return APIResponse.success(data={"message": "待实现"})

    @action(detail=False, methods=["post"])
    def import_(self, request):
        """导入用户 — POST /api/user/import"""
        return APIResponse.success(data={"message": "待实现"})

    @action(detail=False, methods=["post"])
    def avatar(self, request):
        """上传头像 — POST /api/user/avatar"""
        return APIResponse.success(data={"message": "待实现"})

    @action(detail=False, methods=["get", "put"])
    def profile(self, request):
        """个人资料 — GET/PUT /api/user/profile"""
        return APIResponse.success(data={"message": "待实现"})
