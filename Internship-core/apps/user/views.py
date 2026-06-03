"""用户模块视图 — 参考《组织架构模块设计方案.md》第 5.2 节"""
import os
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from utils import APIResponse, HasPermission
from .models import User
from .serializers import (
    LoginSerializer,
    UserSerializer,
    UserListSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    RefreshTokenSerializer,
    UserCreateSerializer,
    UserProfileSerializer,
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
        """
        用户注册 — POST /api/user/register

        Request:  { "username": "admin", "password": "admin123", "nickname": "管理员" }
        Response: { "code": 200, "data": { id, username, nickname, ... } }
        """
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="参数错误", code=2000, http_status=400,
            )

        try:
            user = serializer.save()
        except Exception:
            return APIResponse.conflict(message="用户名已存在")

        # 注册后自动登录，返回 token
        refresh = RefreshToken.for_user(user)
        return APIResponse.success(
            message="注册成功",
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

    @action(detail=False, methods=["post"], permission_classes=[AllowAny], url_path="refresh-token")
    def refresh_token(self, request):
        """
        刷新 Token — POST /api/user/refresh-token

        Request:  { "refresh": "eyJ..." }
        Response: { "code": 200, "data": { "access_token": "eyJ...", "refresh_token": "eyJ..." } }
        """
        serializer = RefreshTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="refresh_token 不能为空", code=2000, http_status=400,
            )

        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
            data = {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            }
            return APIResponse.success(data=data, message="Token 刷新成功")
        except TokenError:
            return APIResponse.error(
                message="refresh_token 无效或已过期，请重新登录",
                code=3002, http_status=401,
            )

    @action(detail=True, methods=["put"])
    def status(self, request, pk=None):
        """修改状态 — PUT /api/user/:id/status"""
        try:
            user = self.get_object()
            status_val = request.data.get("status")
            if status_val not in (0, 1):
                return APIResponse.error(message="状态值无效", code=2000, http_status=400)
            user.status = status_val
            user.save(update_fields=["status"])
            return APIResponse.success(message="状态更新成功")
        except Exception:
            return APIResponse.error(message="用户不存在", code=2004, http_status=404)

    @action(detail=False, methods=["put"], url_path="reset-password")
    def reset_password(self, request):
        """重置密码 — PUT /api/user/reset-password"""
        user_id = request.data.get("userId")
        if not user_id:
            return APIResponse.error(message="userId 不能为空", code=2000, http_status=400)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return APIResponse.error(message="用户不存在", code=2004, http_status=404)
        user.set_password("123456")
        user.save(update_fields=["password"])
        return APIResponse.success(message="密码已重置为 123456")

    @action(detail=False, methods=["put"], url_path="update-password")
    def update_password(self, request):
        """
        修改自己的密码 — PUT /api/user/update-password

        Request:  { "old_password": "old123", "new_password": "new123" }
        Response: { "code": 200, "message": "密码修改成功" }
        """
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="参数错误", code=2000, http_status=400,
            )

        user = request.user
        if not user or not user.is_authenticated:
            return APIResponse.error(
                message="未登录", code=3000, http_status=401,
            )

        # 校验旧密码
        if not user.check_password(serializer.validated_data["old_password"]):
            return APIResponse.error(
                message="旧密码不正确", code=2000, http_status=400,
            )

        # 设置新密码
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return APIResponse.success(message="密码修改成功")

    @action(detail=False, methods=["get"])
    def export(self, request):
        """导出用户 — GET /api/user/export"""
        return APIResponse.success(data={"message": "待实现"})

    @action(detail=False, methods=["post"], url_path="import")
    def import_(self, request):
        """导入用户 — POST /api/user/import"""
        return APIResponse.success(data={"message": "待实现"})

    @action(detail=False, methods=["post"])
    def avatar(self, request):
        """
        上传头像 — POST /api/user/avatar

        Request:  multipart/form-data { file: <image> }
        Response: { "code": 200, "data": { "url": "/media/avatars/xxx.jpg" } }
        """
        user = request.user
        if not user or not user.is_authenticated:
            return APIResponse.error(
                message="未登录", code=3000, http_status=401,
            )

        file = request.FILES.get("file")
        if not file:
            return APIResponse.error(
                message="请选择文件", code=2000, http_status=400,
            )

        if file.size > 2 * 1024 * 1024:
            return APIResponse.error(
                message="文件大小不能超过 2MB", code=2000, http_status=400,
            )

        # 校验文件类型
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            return APIResponse.error(
                message="不支持的文件格式，请上传 JPG/PNG/GIF/WebP", code=2000, http_status=400,
            )

        # 保存文件: media/avatars/<username><ext>
        avatar_dir = os.path.join(settings.MEDIA_ROOT, "avatars")
        os.makedirs(avatar_dir, exist_ok=True)
        filename = f"{user.username}{ext}"
        filepath = os.path.join(avatar_dir, filename)

        with open(filepath, "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)

        # 更新用户头像字段
        url = f"{settings.MEDIA_URL}avatars/{filename}"
        user.avatar = url
        user.save(update_fields=["avatar"])

        return APIResponse.success(
            message="上传成功",
            data={"url": url},
        )

    @action(detail=False, methods=["get", "put"])
    def profile(self, request):
        """
        个人资料 — GET/PUT /api/user/profile

        GET  — 返回当前用户信息
        PUT  — 更新个人资料（昵称、邮箱、手机号等）
        """
        user = request.user
        if not user or not user.is_authenticated:
            return APIResponse.error(
                message="未登录", code=3000, http_status=401,
            )

        if request.method == "GET":
            serializer = UserProfileSerializer(user)
            return APIResponse.success(data=serializer.data)

        # PUT — 部分更新
        serializer = UserProfileSerializer(
            user, data=request.data, partial=True,
        )
        if not serializer.is_valid():
            return APIResponse.error(
                message="参数错误", code=2000, http_status=400,
            )
        serializer.save()
        return APIResponse.success(message="更新成功", data=serializer.data)