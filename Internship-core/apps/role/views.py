"""角色模块视图 — 参考《组织架构模块设计方案.md》第 5.3 节"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.db import transaction
from utils.response import APIResponse
from .models import Role, RoleMenuRelation
from .serializers import (
    RoleSerializer,
    AssignMenuSerializer,
    AssignUserSerializer,
)
from apps.menu.models import Menu
from apps.user.models import User, UserRoleRelation


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(data=serializer.data, message="新增成功")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(data=serializer.data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return APIResponse.success(message="删除成功")

    @action(detail=False, methods=["delete"], url_path="batch")
    def batch(self, request):
        """批量删除 — DELETE /api/role/batch"""
        ids = request.data.get("ids", [])
        if not ids:
            return APIResponse.error(message="ids 不能为空")
        Role.objects.filter(id__in=ids).delete()
        return APIResponse.success(message="批量删除成功")

    @action(detail=False, methods=["get"])
    def all(self, request):
        """获取全部角色（下拉框用）"""
        roles = Role.objects.filter(status=1).order_by("role_sort")
        serializer = RoleSerializer(roles, many=True)
        return APIResponse.success(data=serializer.data)

    @action(detail=True, methods=["put"])
    def status(self, request, pk=None):
        instance = self.get_object()
        status_val = request.data.get("status")
        if status_val not in (0, 1):
            return APIResponse.error(message="状态值无效")
        instance.status = status_val
        instance.save()
        return APIResponse.success(message="状态更新成功")

    @action(detail=True, methods=["get", "put"], url_path="menus")
    def menus(self, request, pk=None):
        """获取/分配角色菜单权限"""
        instance = self.get_object()

        if request.method == "GET":
            menu_ids = RoleMenuRelation.objects.filter(
                role=instance
            ).values_list("menu_id", flat=True)
            return APIResponse.success(data=list(menu_ids))

        # PUT — 分配菜单
        serializer = AssignMenuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        menu_ids = serializer.validated_data["menu_ids"]

        with transaction.atomic():
            RoleMenuRelation.objects.filter(role=instance).delete()
            if menu_ids:
                menus = Menu.objects.filter(id__in=menu_ids)
                relations = [
                    RoleMenuRelation(role=instance, menu=menu)
                    for menu in menus
                ]
                RoleMenuRelation.objects.bulk_create(relations)

        return APIResponse.success(message="菜单权限分配成功")

    @action(detail=True, methods=["get", "put"], url_path="users")
    def users(self, request, pk=None):
        """获取/分配角色下的用户"""
        instance = self.get_object()

        if request.method == "GET":
            user_ids = UserRoleRelation.objects.filter(
                role=instance
            ).values_list("user_id", flat=True)
            return APIResponse.success(data=list(user_ids))

        # PUT — 分配用户
        serializer = AssignUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_ids = serializer.validated_data["user_ids"]

        with transaction.atomic():
            UserRoleRelation.objects.filter(role=instance).delete()
            if user_ids:
                users = User.objects.filter(id__in=user_ids)
                relations = [
                    UserRoleRelation(role=instance, user=user)
                    for user in users
                ]
                UserRoleRelation.objects.bulk_create(relations)

        return APIResponse.success(message="用户分配成功")