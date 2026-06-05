"""用户模块视图 — 参考《组织架构模块设计方案.md》第 5.2 节"""

import os
import openpyxl
from django.http import HttpResponse

from django.conf import settings

from django.utils import timezone

from rest_framework import viewsets, status

from rest_framework.decorators import action

from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from utils import APIResponse, HasPermission

from .models import User, PasswordResetRequest

from .serializers import (

    LoginSerializer,

    UserSerializer,

    UserListSerializer,

    ChangePasswordSerializer,

    ResetPasswordSerializer,

    RefreshTokenSerializer,

    UserCreateSerializer,

    UserUpdateSerializer,

    UserProfileSerializer,

    PasswordResetRequestSerializer,

)

import openpyxl
from io import BytesIO
from django.http import HttpResponse

class UserViewSet(viewsets.ModelViewSet):

    """用户管理 CRUD"""

    queryset = User.objects.select_related("department").all()

    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update", "retrieve"):
            return UserUpdateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message="参数错误", code=2000, http_status=400)
        user = serializer.save()
        # 确保默认密码已设置
        if not user.password:
            user.set_password("123456")
            user.save(update_fields=["password"])
        # 用 UserUpdateSerializer 返回（不含 password 字段）
        result_serializer = UserUpdateSerializer(user)
        return APIResponse.success(message="新增成功", data=result_serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 搜索过滤
        username = request.query_params.get("username", "").strip()
        status_val = request.query_params.get("status")
        department_id = request.query_params.get("department_id")

        if username:
            queryset = queryset.filter(username__icontains=username)
        if status_val is not None and status_val != "":
            queryset = queryset.filter(status=int(status_val))
        if department_id:
            queryset = queryset.filter(department_id=int(department_id))

        queryset = queryset.order_by("-create_time")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return APIResponse.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        if not serializer.is_valid():
            return APIResponse.error(message="参数错误", code=2000, http_status=400)
        serializer.save()
        return APIResponse.success(message="更新成功", data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return APIResponse.success(message="删除成功")

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

        user = self.get_object()

        status_val = request.data.get("status")

        if status_val not in (0, 1):

            return APIResponse.error(message="状态值无效", code=2000, http_status=400)

        user.status = status_val

        user.save(update_fields=["status"])

        return APIResponse.success(message="状态更新成功")

    @action(detail=False, methods=["put"], url_path="reset-password")
    def reset_password(self, request):
        """重置密码 — PUT /api/user/reset-password"""
        user_id = request.data.get("userId")
        new_password = request.data.get("password", "123456")
        if not user_id:
            return APIResponse.error(message="userId 不能为空", code=2000, http_status=400)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return APIResponse.error(message="用户不存在", code=2004, http_status=404)
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return APIResponse.success(message="密码已重置")

    @action(detail=False, methods=["delete"], url_path="batch")
    def batch(self, request):
        """批量删除 — DELETE /api/user/batch"""
        ids = request.data.get("ids", [])
        if not ids:
            return APIResponse.error(message="ids 不能为空")
        User.objects.filter(id__in=ids).delete()
        return APIResponse.success(message="批量删除成功")


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
        """导出用户 Excel — GET /api/user/export"""
        users = User.objects.select_related("department").all().order_by("-create_time")[:10000]
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "用户列表"
        headers = ["用户名", "昵称", "真实姓名", "邮箱", "手机号", "性别", "部门", "状态", "创建时间"]
        ws.append(headers)

        # 表头样式
        from openpyxl.styles import Font, Alignment, Border, Side
        font_bold = Font(name="微软雅黑", size=11, bold=True)
        align_center = Alignment(horizontal="center", vertical="center")
        thin = Side(style="thin")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        for cell in ws[1]:
            cell.font = font_bold
            cell.alignment = align_center
            cell.border = border

        # 数据行
        gender_map = {0: "保密", 1: "男", 2: "女"}
        font_normal = Font(name="微软雅黑", size=11)
        for u in users:
            ws.append([
                u.username, u.nickname, u.real_name, u.email, u.telephone,
                gender_map.get(u.gender, "保密"),
                u.department.dept_name if u.department else "",
                "启用" if u.status else "禁用",
                u.create_time.strftime("%Y-%m-%d %H:%M:%S") if u.create_time else "",
            ])
            for cell in ws[ws.max_row]:
                cell.font = font_normal
                cell.alignment = align_center
                cell.border = border

        # 列宽自适应
        col_widths = [16, 14, 14, 24, 16, 8, 8, 8, 22]
        for i, w in enumerate(col_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

        from io import BytesIO
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        response = HttpResponse(
            buf.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="users.xlsx"'
        return response

    @action(detail=False, methods=["post"], url_path="import")

    def import_(self, request):

        """导入用户 Excel — POST /api/user/import"""

        file = request.FILES.get("file")
        if not file:
            return APIResponse.error(message="请选择文件", code=2000, http_status=400)

        # 校验文件类型
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in (".xlsx", ".xls"):
            return APIResponse.error(message="请上传 .xlsx 或 .xls 格式文件", code=2000, http_status=400)

        try:
            wb = openpyxl.load_workbook(file, read_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
        except Exception:
            return APIResponse.error(message="文件解析失败", code=2000, http_status=400)

        if len(rows) < 2:
            return APIResponse.error(message="文件为空或只有表头", code=2000, http_status=400)

        # 跳过表头，逐行创建用户
        headers = rows[0]
        success_count = 0
        skip_count = 0
        errors = []

        for idx, row in enumerate(rows[1:], start=2):
            if not row or not row[0]:
                continue
            username = str(row[0]).strip()
            if User.objects.filter(username=username).exists():
                skip_count += 1
                continue

            gender_map = {"男": 1, "女": 2, "未知": 0}
            status_map = {"启用": 1, "禁用": 0}

            user = User(
                username=username,
                nickname=str(row[1] or "").strip(),
                real_name=str(row[2] or "").strip(),
                email=str(row[3] or "").strip(),
                telephone=str(row[4] or "").strip(),
                gender=gender_map.get(str(row[5] or "").strip(), 0),
                status=status_map.get(str(row[6] or "").strip(), 1),
            )
            user.set_password("123456")
            try:
                user.save()
                success_count += 1
            except Exception as e:
                errors.append(f"第 {idx} 行 ({username}): {str(e)}")

        return APIResponse.success(
            message=f"导入完成：成功 {success_count} 条，跳过 {skip_count} 条（用户名已存在）",
            data={"success": success_count, "skipped": skip_count, "errors": errors},
        )

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

    @action(detail=False, methods=["post"], permission_classes=[AllowAny], url_path="reset-request")
    def create_reset_request(self, request):
        """创建密码重置请求 — POST /api/user/reset-request"""
        username = request.data.get("username", "").strip()
        if not username:
            return APIResponse.error(message="用户名不能为空", code=2000, http_status=400)
        if not User.objects.filter(username=username).exists():
            return APIResponse.error(message="用户不存在，请确认用户名", code=2004, http_status=404)
        if PasswordResetRequest.objects.filter(username=username, status="pending").exists():
            return APIResponse.error(message="该用户已有待处理的重置请求", code=2000, http_status=400)
        req = PasswordResetRequest.objects.create(username=username)
        return APIResponse.success(message="重置请求已提交，请联系管理员处理", data={"id": req.id})

    @action(detail=False, methods=["get"], url_path="reset-requests")
    def list_reset_requests(self, request):
        """获取密码重置请求列表 — GET /api/user/reset-requests"""
        status_filter = request.query_params.get("status")
        qs = PasswordResetRequest.objects.all()
        if status_filter:
            qs = qs.filter(status=status_filter)
        serializer = PasswordResetRequestSerializer(qs, many=True)
        return APIResponse.success(data=serializer.data)

    @action(detail=False, methods=["put"], url_path="approve-reset")
    def approve_reset(self, request):
        """审批重置请求 — PUT /api/user/approve-reset"""
        request_id = request.data.get("request_id")
        if not request_id:
            return APIResponse.error(message="request_id 不能为空", code=2000, http_status=400)
        try:
            req = PasswordResetRequest.objects.get(id=request_id, status="pending")
        except PasswordResetRequest.DoesNotExist:
            return APIResponse.error(message="请求不存在或已处理", code=2004, http_status=404)

        try:
            user = User.objects.get(username=req.username)
        except User.DoesNotExist:
            return APIResponse.error(message="用户已不存在", code=2004, http_status=404)

        new_password = request.data.get("password", "123456")
        user.set_password(new_password)
        user.save(update_fields=["password"])

        req.status = "approved"
        req.handler = request.user
        req.handled_at = timezone.now()
        req.save(update_fields=["status", "handler", "handled_at"])

        return APIResponse.success(message=f"密码已重置为 {new_password}", data={"new_password": new_password})
