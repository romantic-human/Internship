"""用户模块视图 — 参考《组织架构模块设计方案.md》第 5.2 节"""
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
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
        """
        用户登录 — POST /api/user/login

        Request:  { "username": "admin", "password": "admin123" }
        Response: { "code": 200, "data": { "access_token", "refresh_token", "user" } }
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="参数错误：用户名和密码不能为空", code=2000, http_status=400
            )

        username = serializer.validated_data["username"]
        raw_password = serializer.validated_data["password"]

        # 查找用户
        user = User.objects.filter(username=username).first()
        if not user:
            return APIResponse.error(
                message="用户名或密码错误", code=3000, http_status=401
            )

        # 校验密码 (bcrypt)
        if not user.check_password(raw_password):
            return APIResponse.error(
                message="用户名或密码错误", code=3000, http_status=401
            )

        # 校验状态
        if user.status != 1:
            return APIResponse.error(
                message="该账号已被禁用，请联系管理员", code=2003, http_status=400
            )

        # 更新最后登录时间
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        # 生成 JWT
        refresh = RefreshToken.for_user(user)

        return APIResponse.success(
            message="登录成功",
            data={
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "avatar": user.avatar,
                    "roles": user.role_list,
                    "permissions": user.permission_list,
                },
            },
        )

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
